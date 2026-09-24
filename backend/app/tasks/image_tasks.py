"""Provide image tasks components for the application."""

import time
from PIL import Image

from celery.exceptions import MaxRetriesExceededError
from app.services.ocr_service import perform_ocr
from app.core.celery_app import celery_app
from app.repository.file_repository import get_user_file_by_id
from app.repository.image_analysis_repository import (
    create_image_analysis,
    get_image_analysis_by_file_id,
    update_image_analysis,
)
from app.services.image_description_service import analyze_image
from app.services.qwen_service import MODEL_NAME
from app.tasks.task_handlers import handle_task_failure
from app.utils.file_storage import UPLOAD_STORAGE

from app.database.connection import SessionLocal
from app.core.qwen import load_qwen


@celery_app.task(
    bind=True,
    name="app.tasks.image_tasks.image_description_task",
    queue="image_queue",
    max_retries=3,
)
def image_description_task(
    self,
    file_id: int,
    user_id: int,
):
    """Image description task."""

    db = SessionLocal()

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "message": "Validating image file",
            },
        )

        # -----------------------------------------
        # Get file
        # -----------------------------------------

        file = get_user_file_by_id(
            db=db,
            file_id=file_id,
            owner_id=user_id,
        )

        if not file:
            raise ValueError("File not found")

        if not file.file_type.startswith("image/"):
            raise ValueError("Selected file is not an image")

        # -----------------------------------------
        # Get stored image
        # -----------------------------------------

        relative_path = file.storage_reference.replace(
            "uploads/",
            "",
            1,
        )

        image_path = UPLOAD_STORAGE / relative_path

        if not image_path.exists():
            raise ValueError("Stored image not found")

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 20,
                "message": "Image validated",
            },
        )

        # -----------------------------------------
        # Load Qwen
        # -----------------------------------------

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 30,
                "message": "Loading Qwen model",
            },
        )

        model, processor = load_qwen()

        # -----------------------------------------
        # Run image analysis
        # -----------------------------------------

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 40,
                "message": "Preprocessing image",
            },
        )

        result = analyze_image(
            model=model,
            processor=processor,
            image_path=image_path,
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 80,
                "message": "Saving image description",
            },
        )

        warnings = []

        if not result["resolution_valid"]:
            warnings.append(
                "Image resolution is below the recommended size."
            )

        if result["blur"]["is_blurry"]:
            warnings.append(
                "Image may be blurry."
            )

        # -----------------------------------------
        # Save / update database
        # -----------------------------------------

        existing_analysis = get_image_analysis_by_file_id(
            db=db,
            file_id=file.id,
        )

        if existing_analysis:

            analysis = update_image_analysis(
                db=db,
                image_analysis=existing_analysis,
                description=result["description"],
                model_used=MODEL_NAME,
                status="completed",
                processing_time=result["processing_time"],
                warnings=warnings,
            )

        else:

            analysis = create_image_analysis(
                db=db,
                file_id=file.id,
                description=result["description"],
                model_used=MODEL_NAME,
                status="completed",
                processing_time=result["processing_time"],
                warnings=warnings,
            )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 100,
                "message": "Image description completed",
            },
        )

        return {
            "status": "completed",
            "task_id": self.request.id,
            "file_id": file_id,
            "analysis_id": analysis.id,
            "description": analysis.description,
            "processing_time": analysis.processing_time,
        }

    except Exception as exc:

        handle_task_failure(
            task_name=self.name,
            task_id=self.request.id,
            error=str(exc),
        )

        try:
            raise self.retry(
                exc=exc,
                countdown=10,
            )

        except MaxRetriesExceededError:
            raise

    finally:
        db.close()



@celery_app.task(
    bind=True,
    name="app.tasks.image_tasks.ocr_task",
    queue="image_queue",
    max_retries=3,
)
def ocr_task(
    self,
    file_id: int,
    user_id: int,
):
    """Ocr task."""

    db = SessionLocal()

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "message": "Validating image file",
            },
        )

        # -----------------------------------------
        # Get file
        # -----------------------------------------

        file = get_user_file_by_id(
            db=db,
            file_id=file_id,
            owner_id=user_id,
        )

        if not file:
            raise ValueError("File not found")

        if not file.file_type.startswith("image/"):
            raise ValueError("Selected file is not an image")

        # -----------------------------------------
        # Get stored image
        # -----------------------------------------

        relative_path = file.storage_reference.replace(
            "uploads/",
            "",
            1,
        )

        image_path = UPLOAD_STORAGE / relative_path

        if not image_path.exists():
            raise ValueError("Stored image not found")

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 25,
                "message": "Image validated",
            },
        )

        # -----------------------------------------
        # Open image
        # -----------------------------------------

        try:
            image = Image.open(image_path)
            image.load()
            image = image.convert("RGB")
        except Exception as exc:
            raise ValueError(
                f"Unable to open image: {str(exc)}"
            ) from exc

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 40,
                "message": "Running OCR",
            },
        )

        # -----------------------------------------
        # Run OCR
        # -----------------------------------------

        ocr_result = perform_ocr(
            image=image,
            language="eng",
            psm=None,
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 80,
                "message": "Saving OCR result",
            },
        )

        # -----------------------------------------
        # Save / update database
        # -----------------------------------------

        existing_analysis = get_image_analysis_by_file_id(
            db=db,
            file_id=file.id,
        )

        if existing_analysis:

            analysis = update_image_analysis(
                db=db,
                image_analysis=existing_analysis,
                ocr_text=ocr_result["text"],
                ocr_confidence=ocr_result["confidence"],
                ocr_word_count=ocr_result["word_count"],
                status="completed",
                processing_time=ocr_result["processing_time"],
                warnings=ocr_result["warnings"],
            )

        else:

            analysis = create_image_analysis(
                db=db,
                file_id=file.id,
                ocr_text=ocr_result["text"],
                ocr_confidence=ocr_result["confidence"],
                ocr_word_count=ocr_result["word_count"],
                status="completed",
                processing_time=ocr_result["processing_time"],
                warnings=ocr_result["warnings"],
            )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 100,
                "message": "OCR completed",
            },
        )

        return {
            "status": "completed",
            "task_id": self.request.id,
            "file_id": file_id,
            "analysis_id": analysis.id,
            "ocr_text": analysis.ocr_text,
            "ocr_confidence": analysis.ocr_confidence,
            "ocr_word_count": analysis.ocr_word_count,
            "processing_time": analysis.processing_time,
        }

    except Exception as exc:

        handle_task_failure(
            task_name=self.name,
            task_id=self.request.id,
            error=str(exc),
        )

        try:
            raise self.retry(
                exc=exc,
                countdown=10,
            )

        except MaxRetriesExceededError:
            raise

    finally:
        db.close()
