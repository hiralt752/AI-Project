"""Provide history repository components for the application."""

from sqlalchemy import (
    and_,
    asc,
    desc,
    func,
    or_,
)
from sqlalchemy.orm import Session

from app.models.document_analysis import DocumentAnalysis
from app.models.file import File
from app.models.image_analysis import ImageAnalysis


def _base_history_query(
    db: Session,
):
    """
    Build the base history query.

    Only the latest active analysis for each file
    is returned.

    Analysis ID is used as the latest-record indicator
    because the current ImageAnalysis and DocumentAnalysis
    models do not contain a created_at column.
    """

    # =========================================================
    # LATEST IMAGE ANALYSIS
    # =========================================================

    latest_image_subquery = (
        db.query(
            ImageAnalysis.file_id,

            func.max(
                ImageAnalysis.id
            ).label("latest_id"),
        )
        .filter(
            ImageAnalysis.is_deleted.is_(False),
        )
        .group_by(
            ImageAnalysis.file_id,
        )
        .subquery()
    )

    # =========================================================
    # LATEST DOCUMENT ANALYSIS
    # =========================================================

    latest_document_subquery = (
        db.query(
            DocumentAnalysis.file_id,

            func.max(
                DocumentAnalysis.id
            ).label("latest_id"),
        )
        .filter(
            DocumentAnalysis.is_deleted.is_(False),
        )
        .group_by(
            DocumentAnalysis.file_id,
        )
        .subquery()
    )

    # =========================================================
    # MAIN HISTORY QUERY
    # =========================================================

    query = (
        db.query(
            File,
            ImageAnalysis,
            DocumentAnalysis,
        )

        # -----------------------------------------------------
        # Latest image analysis for each file
        # -----------------------------------------------------

        .outerjoin(
            latest_image_subquery,
            latest_image_subquery.c.file_id
            == File.id,
        )

        .outerjoin(
            ImageAnalysis,
            and_(
                ImageAnalysis.id
                == latest_image_subquery.c.latest_id,

                ImageAnalysis.file_id
                == File.id,

                ImageAnalysis.is_deleted.is_(False),
            ),
        )

        # -----------------------------------------------------
        # Latest document analysis for each file
        # -----------------------------------------------------

        .outerjoin(
            latest_document_subquery,
            latest_document_subquery.c.file_id
            == File.id,
        )

        .outerjoin(
            DocumentAnalysis,
            and_(
                DocumentAnalysis.id
                == latest_document_subquery.c.latest_id,

                DocumentAnalysis.file_id
                == File.id,

                DocumentAnalysis.is_deleted.is_(False),
            ),
        )

        # -----------------------------------------------------
        # Active files only
        # -----------------------------------------------------

        .filter(
            File.is_deleted.is_(False),

            or_(
                ImageAnalysis.id.is_not(None),

                DocumentAnalysis.id.is_not(None),
            ),
        )
    )

    return query


def get_history(
    db: Session,
    owner_id: int,
    page: int,
    page_size: int,
    history_type: str = "all",
    status: str | None = None,
    search: str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
):
    """
    Get paginated history for a specific user.
    """

    query = _base_history_query(
        db
    ).filter(
        File.owner_id == owner_id,
    )

    # =========================================================
    # FILTER BY ANALYSIS TYPE
    # =========================================================

    if history_type == "image":

        query = query.filter(
            ImageAnalysis.id.is_not(None),
        )

    elif history_type == "document":

        query = query.filter(
            DocumentAnalysis.id.is_not(None),
        )

    # =========================================================
    # FILTER BY STATUS
    # =========================================================

    if status:

        query = query.filter(
            func.coalesce(
                ImageAnalysis.status,
                DocumentAnalysis.status,
            )
            == status
        )

    # =========================================================
    # SEARCH BY FILE NAME
    # =========================================================

    if search:

        query = query.filter(
            File.file_name.ilike(
                f"%{search}%"
            ),
        )

    # =========================================================
    # SORTING
    # =========================================================

    if sort_by == "file_name":

        sort_expression = File.file_name

    elif sort_by == "status":

        sort_expression = func.coalesce(
            ImageAnalysis.status,
            DocumentAnalysis.status,
        )

    else:

        # Current models do not have created_at.
        #
        # The latest analysis ID is used as
        # the history ordering field.

        sort_expression = func.coalesce(
            ImageAnalysis.id,
            DocumentAnalysis.id,
            File.id,
        )

    if sort_order == "asc":

        query = query.order_by(
            asc(sort_expression),
        )

    else:

        query = query.order_by(
            desc(sort_expression),
        )

    # =========================================================
    # TOTAL
    # =========================================================

    total = query.count()

    # =========================================================
    # PAGINATION
    # =========================================================

    offset = (
        page - 1
    ) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return rows, total


def get_history_by_file_id(
    db: Session,
    file_id: int,
    owner_id: int,
):
    """
    Get the latest active history record
    for a specific file.
    """

    return (
        _base_history_query(db)
        .filter(
            File.id == file_id,

            File.owner_id == owner_id,
        )
        .first()
    )


def soft_delete_history(
    db: Session,
    file_id: int,
    owner_id: int,
):
    """
    Soft-delete the latest active analysis
    associated with a file.

    The uploaded file itself is not deleted.
    """

    row = get_history_by_file_id(
        db=db,

        file_id=file_id,

        owner_id=owner_id,
    )

    if row is None:

        return None

    (
        file,
        image_analysis,
        document_analysis,
    ) = row

    # =========================================================
    # SELECT ACTIVE ANALYSIS
    # =========================================================

    analysis = (
        image_analysis
        or document_analysis
    )

    if analysis is None:

        return None

    # =========================================================
    # SOFT DELETE
    # =========================================================

    analysis.is_deleted = True

    db.commit()

    db.refresh(
        analysis
    )

    return file, analysis