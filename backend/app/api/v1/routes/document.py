"""Provide document components for the application."""


from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.oauth2 import get_current_user
from app.core.qwen import load_qwen

from app.schema.document import DocumentAnalysisRequest

from app.repository.file_repository import (
    get_user_file_by_id,
)

from app.utils.file_storage import (
    UPLOAD_STORAGE,
)

from app.services.document_service import (
    process_document,
)

from app.services.document_pipeline_service import (
    DocumentPipelineService,
)

from app.services.document_analysis_service import (
    save_document_analysis,
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post("/analyze")
def analyze_document(
    request: DocumentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # =========================================================
    # STEP 1 — GET USER'S FILE
    # =========================================================

    """Analyze an uploaded document for the authenticated user."""

    file = get_user_file_by_id(
        db=db,
        file_id=request.file_id,
        owner_id=current_user.id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    # =========================================================
    # STEP 2 — BUILD PHYSICAL FILE PATH
    # =========================================================

    if not file.storage_reference.startswith("uploads/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file storage reference.",
        )

    relative_path = file.storage_reference.replace(
        "uploads/",
        "",
        1,
    )

    file_path = UPLOAD_STORAGE / relative_path

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Stored file not found.",
        )

    # =========================================================
    # STEP 3 — PROCESS DOCUMENT
    # =========================================================

    try:
        document = process_document(
            str(file_path)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(exc)}",
        ) from exc

    # =========================================================
    # STEP 4 — GET SHARED QWEN MODEL
    # =========================================================

    model, processor = load_qwen()

    # =========================================================
    # STEP 5 — CREATE PIPELINE
    # =========================================================

    pipeline = DocumentPipelineService(
        model=model,
        processor=processor,
    )

    # =========================================================
    # STEP 6 — RUN DOCUMENT PIPELINE & SAVE RESULT TO DATABASE
    # =========================================================

    try:
        result = pipeline.process(
            document=document,
            summary_mode=request.summary_mode,
            extract_structured=request.extract_structured,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(exc)}",
        ) from exc


    try:

        analysis = save_document_analysis(
            db=db,
            file_id=file.id,
            result=result,
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document analysis: {str(exc)}",
        ) from exc


    # =========================================================
    # STEP 7 — RETURN RESULT
    # =========================================================

    return {
        "success": True,
        "message": "Document analyzed successfully.",
        "data": {
            "file_id": file.id,
            "file_name": file.file_name,
            "summary_mode": request.summary_mode,
            **result,
        },
    }
