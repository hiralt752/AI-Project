from pathlib import Path

import cv2
import numpy as np

from PIL import (
    Image,
    ImageEnhance,
    ImageOps,
)




def load_image(
    image_path: str | Path,
) -> Image.Image:
    """
    Load an image using Pillow.

    Raises:
        ValueError: If the image is invalid or corrupted.
    """

    try:
        image = Image.open(image_path)

        # Force Pillow to actually read the image data.
        # This helps detect corrupted files.
        image.load()

        return image

    except Exception as exc:
        raise ValueError(
            "Invalid or corrupted image"
        ) from exc




def validate_image(
    image: Image.Image,
) -> None:
    """
    Validate basic image properties.
    """

    if image.width <= 0:
        raise ValueError(
            "Invalid image width"
        )

    if image.height <= 0:
        raise ValueError(
            "Invalid image height"
        )

    if image.format is None:
        raise ValueError(
            "Invalid image format"
        )




def correct_orientation(
    image: Image.Image,
) -> Image.Image:
    """
    Correct image orientation using EXIF metadata.

    This is useful for images captured using
    mobile phones and cameras.
    """

    return ImageOps.exif_transpose(image)



def convert_to_rgb(
    image: Image.Image,
) -> Image.Image:
    """
    Convert image to RGB format.
    """

    return image.convert("RGB")



def check_resolution(
    image: Image.Image,
    min_width: int = 224,
    min_height: int = 224,
) -> bool:
    """
    Check whether the image meets minimum resolution.
    """

    return (
        image.width >= min_width
        and image.height >= min_height
    )




def check_quality(
    image: Image.Image,
) -> dict:
    """
    Perform a basic image-quality assessment
    based on image resolution.
    """

    width = image.width
    height = image.height

    total_pixels = width * height

    if total_pixels < 224 * 224:
        quality = "low"

    elif total_pixels < 640 * 480:
        quality = "medium"

    else:
        quality = "good"

    return {
        "width": width,
        "height": height,
        "pixels": total_pixels,
        "quality": quality,
    }




def detect_blur(
    image: Image.Image,
    threshold: float = 100.0,
) -> dict:
    """
    Detect image blur using Laplacian variance.

    Higher score  -> generally sharper image
    Lower score   -> generally blurrier image

    Returns:
        {
            "blur_score": float,
            "is_blurry": bool
        }
    """

    image_array = np.array(image)

    gray = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY,
    )

    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F,
    ).var()

    return {
        "blur_score": float(blur_score),
        "is_blurry": blur_score < threshold,
    }




def denoise_image(
    image: Image.Image,
) -> Image.Image:
    """
    Remove noise from the image using OpenCV.
    """

    image_array = np.array(image)

    denoised = cv2.fastNlMeansDenoisingColored(
        image_array,
        None,
        10,
        10,
        7,
        21,
    )

    return Image.fromarray(denoised)




def sharpen_image(
    image: Image.Image,
) -> Image.Image:
    """
    Enhance image edges and sharpness.
    """

    image_array = np.array(image)

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0],
    ])

    sharpened = cv2.filter2D(
        image_array,
        -1,
        kernel,
    )

    return Image.fromarray(sharpened)




def enhance_contrast(
    image: Image.Image,
    factor: float = 1.2,
) -> Image.Image:
    """
    Enhance image contrast.

    factor=1.0 -> original contrast
    factor>1.0 -> increase contrast
    factor<1.0 -> decrease contrast
    """

    enhancer = ImageEnhance.Contrast(
        image
    )

    return enhancer.enhance(factor)




def resize_image(
    image: Image.Image,
    max_size: int = 1024,
) -> Image.Image:
    """
    Resize image while preserving aspect ratio.

    Example:

        1920x1080
            ↓
        1024x576

    instead of:

        1920x1080
            ↓
        1024x1024
    """

    image = image.copy()

    image.thumbnail(
        (max_size, max_size),
        Image.Resampling.LANCZOS,
    )

    return image




def normalize_image(
    image: Image.Image,
) -> np.ndarray:
    """
    Convert image pixel values from:

        0 - 255

    to:

        0.0 - 1.0

    Returns:
        NumPy array with float32 values.
    """

    image_array = np.array(
        image,
        dtype=np.float32,
    )

    normalized = image_array / 255.0

    return normalized