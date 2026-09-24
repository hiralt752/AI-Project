"""Provide image processing service components for the application."""

from pathlib import Path

from app.utils.image_processing import (
    load_image,
    validate_image,
    correct_orientation,
    convert_to_rgb,
    check_resolution,
    check_quality,
    detect_blur,
    denoise_image,
    sharpen_image,
    enhance_contrast,
    resize_image,
)


def preprocess_image(image_path: str | Path) -> dict:
    
    """Preprocess an image for analysis."""

    image = load_image(image_path)

    

    validate_image(image)

   

    image = correct_orientation(image)

   

    image = convert_to_rgb(image)

    

    resolution_valid = check_resolution(image)

   

    quality_result = check_quality(image)

    

    blur_result = detect_blur(image)

   

    image = denoise_image(image)

    

    image = sharpen_image(image)

   

    image = enhance_contrast(image)


    image = resize_image(image)

    #normalized_image = normalize_image(image)

    

    return {
        "image": image,
        #"normalized_image": normalized_image,
        "resolution_valid": resolution_valid,
        "quality": quality_result,
        "blur": blur_result,
    }
