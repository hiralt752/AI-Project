"""Provide document components for the application."""


from sqlalchemy.orm import Session

from app.models.document_analysis import DocumentAnalysis


def create_document_analysis(
    db: Session,
    file_id: int,
    summary_mode: str,
    summary: str | None = None,
    key_points: list | None = None,
    entities: list | None = None,
    decisions: list | None = None,
    action_items: list | None = None,
    chunk_count: int | None = None,
    chunk_summaries: list | None = None,
    model_used: str | None = None,
    status: str = "completed",
    processing_time: float | None = None,
    warnings: list | None = None,
) -> DocumentAnalysis:
    """
    Create a new document analysis record.
    """

    analysis = DocumentAnalysis(
        file_id=file_id,
        summary_mode=summary_mode,
        summary=summary,
        key_points=key_points,
        entities=entities,
        decisions=decisions,
        action_items=action_items,
        chunk_count=chunk_count,
        chunk_summaries=chunk_summaries,
        model_used=model_used,
        status=status,
        processing_time=processing_time,
        warnings=warnings,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


def get_document_analysis_by_id(
    db: Session,
    analysis_id: int,
) -> DocumentAnalysis | None:
    """
    Get a document analysis by its ID.
    """

    return (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.id == analysis_id,
            DocumentAnalysis.is_deleted.is_(False),
        )
        .first()
    )


def get_document_analysis_by_file_id(
    db: Session,
    file_id: int,
) -> DocumentAnalysis | None:
    """
    Get the latest active analysis for a file.
    """

    return (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.file_id == file_id,
            DocumentAnalysis.is_deleted.is_(False),
        )
        .order_by(DocumentAnalysis.id.desc())
        .first()
    )


def get_all_document_analyses(
    db: Session,
) -> list[DocumentAnalysis]:
    """
    Get all active document analysis records.
    """

    return (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.is_deleted.is_(False),
        )
        .order_by(DocumentAnalysis.id.desc())
        .all()
    )


def update_document_analysis(
    db: Session,
    analysis: DocumentAnalysis,
    **fields,
) -> DocumentAnalysis:
    """
    Update fields of an existing document analysis.
    """

    for field, value in fields.items():

        if hasattr(DocumentAnalysis, field):
            setattr(analysis, field, value)

    db.commit()
    db.refresh(analysis)

    return analysis


def update_document_analysis_status(
    db: Session,
    analysis: DocumentAnalysis,
    status: str,
    warnings: list | None = None,
) -> DocumentAnalysis:
    """
    Update analysis status and warnings.
    """

    analysis.status = status

    if warnings is not None:
        analysis.warnings = warnings

    db.commit()
    db.refresh(analysis)

    return analysis


def soft_delete_document_analysis(
    db: Session,
    analysis: DocumentAnalysis,
) -> DocumentAnalysis:
    """
    Soft-delete a document analysis record.
    """

    analysis.is_deleted = True

    db.commit()
    db.refresh(analysis)

    return analysis
