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

from app.utils.file_storage import UPLOAD_STORAGE
from app.utils.ocr import extract_text_with_confidence




def perform_ocr(
    image: Image.Image,
    language: str = "eng",
    psm: int | None = None,
) -> dict:
    """
    Common OCR service.

    Used by:
    1. Standalone OCR
    2. Analyze Both

    This function performs OCR only.
    It does NOT access the database.
    """

    if image is None:
        raise ValueError(
            "Image is required for OCR"
        )

    start_time = time.time()

    try:
        ocr_result = extract_text_with_confidence(
            image=image,
            language=language,
            psm=psm,
        )

    except Exception as exc:
        raise RuntimeError(
            f"OCR processing failed: {str(exc)}"
        ) from exc

    processing_time = time.time() - start_time

    warnings = []

    # No text found
    if not ocr_result["text"]:
        warnings.append(
            "No text detected in image."
        )

    # Low confidence
    if ocr_result["confidence"] < 50:
        warnings.append(
            "OCR confidence is low."
        )

    return {
        "text": ocr_result["text"],
        "confidence": ocr_result["confidence"],
        "word_count": ocr_result["word_count"],
        "processing_time": processing_time,
        "warnings": warnings,
    }




def perform_uploaded_image_ocr_service(
    db: Session,
    file_id: int,
    user_id: int,
    language: str = "eng",
    psm: int | None = None,
):
    """
    Standalone OCR service.

    Responsibilities:
    - Find user's file
    - Validate file
    - Find stored image
    - Open image
    - Call common perform_ocr()
    - Save OCR result in database
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
        image = Image.open(image_path)

        # Force PIL to load the image completely
        image.load()

        # Convert RGBA, P, L, etc. to RGB
        image = image.convert("RGB")

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to open image: {str(exc)}",
        ) from exc

    

    try:
        ocr_result = perform_ocr(
            image=image,
            language=language,
            psm=psm,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(exc)}",
        ) from exc

    

    processing_time = time.time() - start_time

    

    existing_analysis = get_image_analysis_by_file_id(
        db=db,
        file_id=file.id,
    )


    if existing_analysis:

        return update_image_analysis(
            db=db,
            image_analysis=existing_analysis,
            ocr_text=ocr_result["text"],
            ocr_confidence=ocr_result["confidence"],
            ocr_word_count=ocr_result["word_count"],
            status="completed",
            processing_time=processing_time,
            warnings=ocr_result["warnings"],
        )

   

    return create_image_analysis(
        db=db,
        file_id=file.id,
        ocr_text=ocr_result["text"],
        ocr_confidence=ocr_result["confidence"],
        ocr_word_count=ocr_result["word_count"],
        status="completed",
        processing_time=processing_time,
        warnings=ocr_result["warnings"],
    )

