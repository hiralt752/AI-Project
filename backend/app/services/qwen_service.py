import torch
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from app.utils.description_validator import validate_description


MODEL_NAME = "Qwen/Qwen3-VL-2B-Instruct"


def load_qwen_model():
    print("Loading Qwen3-VL-2B-Instruct...")

    model = Qwen3VLForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        device_map="cpu",
    )

    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    model.eval()

    print("Qwen3-VL model loaded successfully.")

    return model, processor


def describe_image(
    model,
    processor,
    image,
    prompt: str = "Describe this image in detail.",
):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image,
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    inputs = {
        key: value.to("cpu") if hasattr(value, "to") else value
        for key, value in inputs.items()
    }

    print("Generating description...")

    try:
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=False,
        )

    except RuntimeError as exc:
        raise RuntimeError(
            f"Qwen inference failed: {str(exc)}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
        f"Unexpected Qwen inference error: {str(exc)}"
    ) from exc

    generated_ids_trimmed = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(
            inputs["input_ids"],
            generated_ids,
        )
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )

    description = validate_description(output_text[0])

    return description