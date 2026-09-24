"""Provide image description service components for the application."""


import time
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.image_processing_service import preprocess_image
from app.services.qwen_service import describe_image, MODEL_NAME

from app.repository.file_repository import get_user_file_by_id
from app.repository.image_analysis_repository import (
    create_image_analysis,
    get_image_analysis_by_file_id,
    update_image_analysis,
)

from app.utils.file_storage import UPLOAD_STORAGE


def analyze_image(
    model,
    processor,
    image_path: str | Path,
    prompt: str = (
        "Describe this image clearly and in detail. "
        "Mention the main objects, people, environment, "
        "actions, colors, and any visible text."
    ),
):
    """Analyze image."""

    start_time = time.time()

    # Preprocess image
    preprocessing_result = preprocess_image(image_path)

    # Get processed PIL image
    processed_image = preprocessing_result["image"]

    # Send processed image to Qwen
    description = describe_image(
        model=model,
        processor=processor,
        image=processed_image,
        prompt=prompt,
    )

    processing_time = time.time() - start_time

    return {
        "description": description,
        "processing_time": processing_time,
        "resolution_valid": preprocessing_result["resolution_valid"],
        "quality": preprocessing_result["quality"],
        "blur": preprocessing_result["blur"],
    }


def describe_uploaded_image_service(
    db: Session,
    file_id: int,
    user_id: int,
    model,
    processor,
):
    # 1. Get uploaded file belonging to current user
    """Describe uploaded image service."""

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

    # 2. Check whether the file is an image
    if not file.file_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Selected file is not an image",
        )

    # 3. Get stored image path
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

    # 4. Run Qwen image analysis
    try:
        result = analyze_image(
            model=model,
            processor=processor,
            image_path=image_path,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image description failed: {str(exc)}",
        ) from exc

    # 5. Prepare warnings
    warnings = []

    if not result["resolution_valid"]:
        warnings.append(
            "Image resolution is below the recommended size."
        )

    if result["blur"]["is_blurry"]:
        warnings.append(
            "Image may be blurry."
        )

    # 6. Check whether analysis already exists
    existing_analysis = get_image_analysis_by_file_id(
        db=db,
        file_id=file.id,
    )

    # 7. Update existing analysis
    if existing_analysis:
        return update_image_analysis(
            db=db,
            image_analysis=existing_analysis,
            description=result["description"],
            model_used=MODEL_NAME,
            status="completed",
            processing_time=result["processing_time"],
            warnings=warnings,
        )

    # 8. Create new analysis
    return create_image_analysis(
        db=db,
        file_id=file.id,
        description=result["description"],
        model_used=MODEL_NAME,
        status="completed",
        processing_time=result["processing_time"],
        warnings=warnings,
    )

