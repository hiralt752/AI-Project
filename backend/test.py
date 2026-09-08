import time

from app.services.qwen_service import load_qwen_model
from app.services.image_description_service import analyze_image


print("Starting complete image analysis test...")

# Load model
start_time = time.time()

model, processor = load_qwen_model()

load_time = time.time() - start_time

print(f"Model loading time: {load_time:.2f} seconds")


# Analyze image
print("\nStarting image preprocessing + Qwen analysis...")

result = analyze_image(
    model=model,
    processor=processor,
    image_path="storage/uploads/801f5f93-a9ef-47a3-a541-2df1a1bae406.png",
)


# Display result
print("\n========== RESULT ==========")

print("\nDescription:")
print(result["description"])

print("\nResolution valid:")
print(result["resolution_valid"])

print("\nQuality:")
print(result["quality"])

print("\nBlur:")
print(result["blur"])

print("\nProcessing time:")
print(f"{result['processing_time']:.2f} seconds")

print("============================")