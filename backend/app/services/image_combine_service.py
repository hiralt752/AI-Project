"""Provide image combine service components for the application."""

import time

from fastapi import HTTPException
from PIL import Image
from sqlalchemy.orm import Session

from app.repository.file_repository import get_user_file_by_id

from app.repository.image_analysis_repository import (
    create_image_analysis,
    get_image_analysis_by_file_id,
    update_image_analysis,
)

from app.services.image_description_service import analyze_image
from app.services.ocr_service import perform_ocr
from app.services.qwen_service import MODEL_NAME

from app.utils.file_storage import UPLOAD_STORAGE




def analyze_both_service(
    db: Session,
    file_id: int,
    user_id: int,
    model,
    processor,
):
    """
    Performs:

    1. Image description using Qwen
    2. OCR using Tesseract
    3. Combines both results
    4. Saves result into image_analyses
    """

    start_time = time.time()

    

    file = get_user_file_by_id(
        db=db,
        file_id=file_id,
        owner_id=user_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )


    if not file.file_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Selected file is not an image",
        )

    

    relative_path = file.storage_reference.replace(
        "uploads/",
        "",
        1,
    )

    image_path = UPLOAD_STORAGE / relative_path

    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Stored image not found",
        )

    

    try:
        qwen_result = analyze_image(
            model=model,
            processor=processor,
            image_path=image_path,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image description failed: {str(exc)}",
        ) from exc

    

    try:
        image = Image.open(image_path)

        # Load image completely
        image.load()

        # Convert different image modes to RGB
        image = image.convert("RGB")

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to open image: {str(exc)}",
        ) from exc

    

    try:
        # IMPORTANT:
        #
        # Do NOT call:
        #
        # perform_uploaded_image_ocr_service()
        #
        # because that function performs its own
        # file lookup and database operation.
        #
        # Instead use the common OCR function.

        ocr_result = perform_ocr(
            image=image,
            language="eng",
            psm=None,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(exc)}",
        ) from exc

   
    processing_time = time.time() - start_time


    warnings = []

    # Qwen image quality warnings
    if not qwen_result["resolution_valid"]:

        warnings.append(
            "Image resolution is below the recommended size."
        )

    if qwen_result["blur"]["is_blurry"]:

        warnings.append(
            "Image may be blurry."
        )

    # OCR warnings
    warnings.extend(
        ocr_result["warnings"]
    )

    

    existing_analysis = get_image_analysis_by_file_id(
        db=db,
        file_id=file.id,
    )

   

    if existing_analysis:

        return update_image_analysis(
            db=db,
            image_analysis=existing_analysis,
            description=qwen_result["description"],
            ocr_text=ocr_result["text"],
            ocr_confidence=ocr_result["confidence"],
            ocr_word_count=ocr_result["word_count"],
            model_used=MODEL_NAME,
            status="completed",
            processing_time=processing_time,
            warnings=warnings,
        )

    

    return create_image_analysis(
        db=db,
        file_id=file.id,
        description=qwen_result["description"],
        ocr_text=ocr_result["text"],
        ocr_confidence=ocr_result["confidence"],
        ocr_word_count=ocr_result["word_count"],
        model_used=MODEL_NAME,
        status="completed",
        processing_time=processing_time,
        warnings=warnings,
    )

