import time
from pathlib import Path

from app.services.image_processing_service import preprocess_image
from app.services.qwen_service import describe_image


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