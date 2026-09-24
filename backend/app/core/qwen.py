"""Provide qwen components for the application."""

from app.services.qwen_service import load_qwen_model


model = None
processor = None


def load_qwen():
    """Load and cache the shared Qwen model and processor."""

    global model, processor

    if model is None or processor is None:
        model, processor = load_qwen_model()

    return model, processor
