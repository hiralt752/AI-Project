"""Provide history service components for the application."""

from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.history import (
    get_history,
    get_history_by_file_id,
    soft_delete_history,
)
from app.schema.history import (
    HistoryDeleteResponse,
    HistoryDetailResponse,
    HistoryListItem,
    HistoryListResponse,
)


def _get_analysis_type(
    image_analysis,
    document_analysis,
) -> str:
    """Determine whether a history item is image or document."""

    if image_analysis is not None:
        return "image"

    if document_analysis is not None:
        return "document"

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis result not found.",
    )


def _build_list_item(
    file,
    image_analysis,
    document_analysis,
) -> HistoryListItem:
    """
    Build a history list item with the complete analysis result.

    Image files return image analysis fields.

    Document files return document summarization
    and structured extraction fields.
    """

    # =========================================================
    # IMAGE ANALYSIS
    # =========================================================

    if image_analysis is not None:

        return HistoryListItem(
            id=file.id,
            file_id=file.id,

            file_name=file.file_name,
            file_type=file.file_type,

            analysis_type="image",
            status=image_analysis.status,

            # -------------------------------------------------
            # Image result
            # -------------------------------------------------

            description=image_analysis.description,

            ocr_text=image_analysis.ocr_text,

            ocr_confidence=image_analysis.ocr_confidence,

            ocr_word_count=image_analysis.ocr_word_count,

            detected_objects=image_analysis.detected_objects,

            # -------------------------------------------------
            # Common analysis information
            # -------------------------------------------------

            model_used=image_analysis.model_used,

            processing_time=image_analysis.processing_time,

            warnings=image_analysis.warnings,
        )

    # =========================================================
    # DOCUMENT ANALYSIS
    # =========================================================

    if document_analysis is not None:

        return HistoryListItem(
            id=file.id,
            file_id=file.id,

            file_name=file.file_name,
            file_type=file.file_type,

            analysis_type="document",
            status=document_analysis.status,

            # -------------------------------------------------
            # Document result
            # -------------------------------------------------

            summary_mode=document_analysis.summary_mode,

            summary=document_analysis.summary,

            key_points=document_analysis.key_points,

            entities=document_analysis.entities,

            decisions=document_analysis.decisions,

            action_items=document_analysis.action_items,

            chunk_count=document_analysis.chunk_count,

            chunk_summaries=document_analysis.chunk_summaries,

            # -------------------------------------------------
            # Common analysis information
            # -------------------------------------------------

            model_used=document_analysis.model_used,

            processing_time=document_analysis.processing_time,

            warnings=document_analysis.warnings,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis result not found.",
    )


def _build_detail_response(
    file,
    image_analysis,
    document_analysis,
) -> HistoryDetailResponse:
    """
    Build the complete history detail response.
    """

    # =========================================================
    # IMAGE ANALYSIS
    # =========================================================

    if image_analysis is not None:

        return HistoryDetailResponse(
            id=file.id,

            file_id=file.id,

            # -------------------------------------------------
            # File information
            # -------------------------------------------------

            file_name=file.file_name,

            file_type=file.file_type,

            file_size=file.size,

            storage_reference=file.storage_reference,

            checksum=file.checksum,

            # -------------------------------------------------
            # Analysis information
            # -------------------------------------------------

            analysis_type="image",

            status=image_analysis.status,

            # -------------------------------------------------
            # Image result
            # -------------------------------------------------

            description=image_analysis.description,

            ocr_text=image_analysis.ocr_text,

            ocr_confidence=image_analysis.ocr_confidence,

            ocr_word_count=image_analysis.ocr_word_count,

            detected_objects=image_analysis.detected_objects,

            # -------------------------------------------------
            # Common
            # -------------------------------------------------

            model_used=image_analysis.model_used,

            processing_time=image_analysis.processing_time,

            warnings=image_analysis.warnings,
        )

    # =========================================================
    # DOCUMENT ANALYSIS
    # =========================================================

    if document_analysis is not None:

        return HistoryDetailResponse(
            id=file.id,

            file_id=file.id,

            # -------------------------------------------------
            # File information
            # -------------------------------------------------

            file_name=file.file_name,

            file_type=file.file_type,

            file_size=file.size,

            storage_reference=file.storage_reference,

            checksum=file.checksum,

            # -------------------------------------------------
            # Analysis information
            # -------------------------------------------------

            analysis_type="document",

            status=document_analysis.status,

            # -------------------------------------------------
            # Document result
            # -------------------------------------------------

            summary_mode=document_analysis.summary_mode,

            summary=document_analysis.summary,

            key_points=document_analysis.key_points,

            entities=document_analysis.entities,

            decisions=document_analysis.decisions,

            action_items=document_analysis.action_items,

            chunk_count=document_analysis.chunk_count,

            chunk_summaries=document_analysis.chunk_summaries,

            # -------------------------------------------------
            # Common
            # -------------------------------------------------

            model_used=document_analysis.model_used,

            processing_time=document_analysis.processing_time,

            warnings=document_analysis.warnings,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis result not found.",
    )


def get_history_service(
    db: Session,
    owner_id: int,
    page: int,
    page_size: int,
    history_type: str = "all",
    status_filter: str | None = None,
    search: str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
) -> HistoryListResponse:
    """
    Get paginated history for the current user.
    """

    rows, total = get_history(
        db=db,
        owner_id=owner_id,
        page=page,
        page_size=page_size,
        history_type=history_type,
        status=status_filter,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    items = [
        _build_list_item(
            file=file,
            image_analysis=image_analysis,
            document_analysis=document_analysis,
        )
        for file, image_analysis, document_analysis in rows
    ]

    total_pages = (
        ceil(total / page_size)
        if total
        else 0
    )

    return HistoryListResponse(
        items=items,

        page=page,

        page_size=page_size,

        total=total,

        total_pages=total_pages,
    )


def get_history_detail_service(
    db: Session,
    file_id: int,
    owner_id: int,
) -> HistoryDetailResponse:
    """
    Get the complete analysis result for a file.
    """

    row = get_history_by_file_id(
        db=db,
        file_id=file_id,
        owner_id=owner_id,
    )

    if row is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found.",
        )

    (
        file,
        image_analysis,
        document_analysis,
    ) = row

    return _build_detail_response(
        file=file,

        image_analysis=image_analysis,

        document_analysis=document_analysis,
    )


def delete_history_service(
    db: Session,
    file_id: int,
    owner_id: int,
) -> HistoryDeleteResponse:
    """
    Soft-delete a history record.

    The uploaded file itself is not deleted.
    """

    result = soft_delete_history(
        db=db,
        file_id=file_id,
        owner_id=owner_id,
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found.",
        )

    file, _analysis = result

    return HistoryDeleteResponse(
        message="History record deleted successfully.",

        id=file.id,

        file_id=file.id,
    )