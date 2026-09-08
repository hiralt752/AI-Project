from app.services.qwen_service import load_qwen_model


model = None
processor = None


def load_qwen():
    global model, processor

    if model is None or processor is None:
        model, processor = load_qwen_model()

    return model, processor