"""Provide document tasks components for the application."""

import time

from celery.exceptions import MaxRetriesExceededError

from app.core.celery_app import celery_app
from app.database.connection import SessionLocal

from app.repository.file_repository import get_user_file_by_id

from app.tasks.task_handlers import handle_task_failure

from app.utils.file_storage import UPLOAD_STORAGE


@celery_app.task(
    bind=True,
    name="app.tasks.document_tasks.document_processing_task",
    queue="document_queue",
    max_retries=3,
)
def document_processing_task(
    self,
    file_id: int,
    user_id: int,
):
    """Document processing task."""

    db = SessionLocal()
    start_time = time.time()

    try:
        # --------------------------------
        # 1. Validate document
        # --------------------------------
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "message": "Validating document",
            },
        )

        file = get_user_file_by_id(
            db=db,
            file_id=file_id,
            owner_id=user_id,
        )

        if not file:
            raise ValueError("File not found")

        allowed_document_types = {
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
        }

        if file.file_type not in allowed_document_types:
            raise ValueError(
                "Selected file is not a supported document"
            )

        # --------------------------------
        # 2. Get document path
        # --------------------------------
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 20,
                "message": "Locating document",
            },
        )

        relative_path = file.storage_reference.replace(
            "uploads/",
            "",
            1,
        )

        document_path = UPLOAD_STORAGE / relative_path

        if not document_path.exists():
            raise ValueError("Stored document not found")

        # --------------------------------
        # 3. Document validated
        # --------------------------------
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 30,
                "message": "Document validated",
            },
        )

        # --------------------------------
        # Temporary processing
        # --------------------------------
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 50,
                "message": "Document processing started",
            },
        )

        # --------------------------------
        # TODO:
        # Add document extraction here
        # --------------------------------

        processing_time = time.time() - start_time

        # --------------------------------
        # Completed
        # --------------------------------
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 100,
                "message": "Document processing completed",
            },
        )

        return {
            "status": "completed",
            "task_id": self.request.id,
            "file_id": file_id,
            "file_name": file.file_name,
            "file_type": file.file_type,
            "processing_time": processing_time,
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
