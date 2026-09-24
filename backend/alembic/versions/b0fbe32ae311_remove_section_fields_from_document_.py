"""Remove section fields from document analyses."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b0fbe32ae311"
down_revision: Union[str, Sequence[str], None] = "bda74224afaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unused section-related columns."""
    op.drop_column(
        "document_analyses",
        "section_summaries",
    )

    op.drop_column(
        "document_analyses",
        "section_count",
    )


def downgrade() -> None:
    """Restore section-related columns."""

    pass
        