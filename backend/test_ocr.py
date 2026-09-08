from PIL import Image

from app.services.ocr_service import perform_ocr


IMAGE_PATH = "storage/uploads/801f5f93-a9ef-47a3-a541-2df1a1bae406.png"

image = Image.open(IMAGE_PATH).convert("RGB")

result = perform_ocr(
    image=image,
    language="eng",
    psm=6,
)

print("\n========== OCR RESULT ==========")
print("Text:", result["text"])
print("Has Text:", result["has_text"])
print("Confidence:", result["confidence"])
print("Word Count:", result["word_count"])
print("Language:", result["language"])
print("PSM:", result["psm"])
print("Error:", result["error"])