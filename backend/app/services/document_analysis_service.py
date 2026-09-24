"""Provide document analysis service components for the application."""

from sqlalchemy.orm import Session

from app.repository.document import (
    create_document_analysis,
)


def save_document_analysis(
    db: Session,
    file_id: int,
    result: dict,
):
    """
    Save the final document pipeline result
    into the document_analyses table.
    """

    analysis = create_document_analysis(
        db=db,
        file_id=file_id,

        summary_mode=result.get(
            "summary_mode",
            "Standard",
        ),

        summary=result.get(
            "summary"
        ),

        key_points=result.get(
            "key_points",
            [],
        ),

        section_summaries=result.get(
            "section_summaries",
            [],
        ),

        entities=result.get(
            "entities",
            [],
        ),

        decisions=result.get(
            "decisions",
            [],
        ),

        action_items=result.get(
            "action_items",
            [],
        ),

        chunk_count=result.get(
            "chunk_count"
        ),

        section_count=result.get(
            "section_count"
        ),

        chunk_summaries=result.get(
            "chunk_summaries",
            [],
        ),

        model_used=result.get(
            "model_used"
        ),

        status=result.get(
            "status",
            "completed",
        ),

        processing_time=result.get(
            "processing_time"
        ),

        warnings=result.get(
            "warnings",
            [],
        ),
    )

    return analysis
