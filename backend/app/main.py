"""Provide main components for the application."""

from app.api.v1.routes.auth import router as auth_router
from fastapi import FastAPI
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.files import router as file
from app.api.v1.routes.image import router as images_router
from app.api.v1.routes.document import router as document_router
from app.api.v1.routes.history import router as history_router

app = FastAPI(title="AI Image Description & Document Summarization",)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(file)
app.include_router(images_router)
app.include_router(document_router)
app.include_router(history_router)
