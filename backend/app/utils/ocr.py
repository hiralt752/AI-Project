
import cv2
import numpy as np
import pytesseract

from PIL import Image, ImageOps
from pytesseract import Output



TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH




def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Basic OCR preprocessing.

    Steps:
    - Correct image orientation
    - Convert to RGB
    - Convert to grayscale
    - Upscale small images
    - Improve contrast
    - Reduce noise
    - Sharpen image
    """

    # Correct EXIF orientation
    image = ImageOps.exif_transpose(image)

    # Convert image to RGB
    image = image.convert("RGB")

    # PIL -> NumPy
    image_array = np.array(image)

    # RGB -> Grayscale
    gray = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY,
    )

    

    height, width = gray.shape

    # Small text benefits significantly from upscaling.
    if width < 1200:

        scale = 2

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    

    gray = cv2.normalize(
        gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

   

    sharpen_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )

    gray = cv2.filter2D(
        gray,
        -1,
        sharpen_kernel,
    )

    return gray




def create_ocr_variants(
    image: Image.Image,
) -> list[np.ndarray]:

    gray = preprocess_image(image)

    variants = []

   
    variants.append(gray)

    

    _, otsu = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    variants.append(otsu)

    
    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    variants.append(adaptive)

    return variants



def run_tesseract(
    image: np.ndarray,
    language: str = "eng",
    psm: int = 6,
) -> dict:

    config = (
        f"--oem 3 --psm {psm}"
    )

    data = pytesseract.image_to_data(
        image,
        lang=language,
        config=config,
        output_type=Output.DICT,
    )

    words = []
    confidences = []

    for text, confidence in zip(
        data["text"],
        data["conf"],
    ):

        text = text.strip()

        try:
            confidence = float(confidence)

        except (
            ValueError,
            TypeError,
        ):
            continue

        # Tesseract sometimes returns -1
        # for non-text regions.
        if (
            text
            and confidence >= 0
        ):
            words.append(text)
            confidences.append(confidence)

    extracted_text = " ".join(words)

    # Calculate average confidence
    average_confidence = (
        sum(confidences)
        / len(confidences)
        if confidences
        else 0.0
    )

    return {
        "text": extracted_text,
        "confidence": round(
            average_confidence,
            2,
        ),
        "word_count": len(words),
    }




def calculate_result_score(
    result: dict,
) -> float:

    text = result["text"]
    confidence = result["confidence"]
    word_count = result["word_count"]

    if not text:
        return 0.0

    # Confidence is the most important factor.
    score = confidence * 0.75

    # Reward useful extracted words.
    score += min(
        word_count,
        100,
    ) * 0.25

    return score




def extract_text_with_confidence(
    image: Image.Image,
    language: str = "eng",
    psm: int | None = None,
) -> dict:
    """
    Extract text from an image.

    If psm is provided:
        Only that PSM mode is used.

    If psm is None:
        Multiple PSM modes are tested and
        the best result is selected.
    """

    if image is None:
        raise ValueError(
            "Image is required for OCR"
        )

    
    if psm is not None:

        psm_modes = [psm]

    else:

        # Different image layouts:
        #
        # 6  = single uniform block
        # 11 = sparse text
        # 12 = sparse text + orientation
        #
        # These are useful for general images.
        psm_modes = [
            6,
            11,
            12,
        ]

    

    variants = create_ocr_variants(
        image
    )

    best_result = {
        "text": "",
        "confidence": 0.0,
        "word_count": 0,
    }

    best_score = 0.0

    

    for variant in variants:

        for current_psm in psm_modes:

            try:

                result = run_tesseract(
                    image=variant,
                    language=language,
                    psm=current_psm,
                )

            except Exception:
                continue

            score = calculate_result_score(
                result
            )

            if score > best_score:

                best_score = score

                best_result = result

    

    return {
        "text": best_result["text"],
        "confidence": best_result["confidence"],
        "word_count": best_result["word_count"],
    }

