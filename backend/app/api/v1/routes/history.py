"""Provide history API routes for the application."""

from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.database.connection import get_db
from app.schema.history import (
    HistoryDeleteResponse,
    HistoryDetailResponse,
    HistoryListResponse,
)
from app.services.history_service import (
    delete_history_service,
    get_history_detail_service,
    get_history_service,
)


router = APIRouter(
    prefix="/api/v1/history",
    tags=["History"],
)


@router.get(
    "",
    response_model=HistoryListResponse,
)
def get_history(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number.",
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page.",
    ),

    history_type: Literal[
        "all",
        "image",
        "document",
    ] = Query(
        default="all",
        alias="type",
        description="Filter history by analysis type.",
    ),

    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by analysis status.",
    ),

    search: str | None = Query(
        default=None,
        description="Search history by file name.",
    ),

    sort_by: Literal[
        "id",
        "file_name",
        "status",
    ] = Query(
        default="id",
        description="Field used for sorting.",
    ),

    sort_order: Literal[
        "asc",
        "desc",
    ] = Query(
        default="desc",
        description="Sorting direction.",
    ),

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),
):
    """
    Get paginated history for the
    current authenticated user.
    """

    return get_history_service(
        db=db,

        owner_id=current_user.id,

        page=page,

        page_size=page_size,

        history_type=history_type,

        status_filter=status_filter,

        search=search,

        sort_by=sort_by,

        sort_order=sort_order,
    )


@router.get(
    "/{history_id}",
    response_model=HistoryDetailResponse,
)
def get_history_detail(
    history_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),
):
    """
    Get the complete analysis result
    for a history item.
    """

    return get_history_detail_service(
        db=db,

        file_id=history_id,

        owner_id=current_user.id,
    )


@router.delete(
    "/{history_id}",
    response_model=HistoryDeleteResponse,
)
def delete_history(
    history_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),
):
    """
    Soft-delete a history item.
    """

    return delete_history_service(
        db=db,

        file_id=history_id,

        owner_id=current_user.id,
    )