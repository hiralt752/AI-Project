"""Provide task handlers components for the application."""

import logging


logger = logging.getLogger(__name__)


def handle_task_failure(
    task_name: str,
    task_id: str,
    error: str,
):
    """Handle task failure."""

    logger.error(
        "Task failed | "
        "name=%s | "
        "id=%s | "
        "error=%s",
        task_name,
        task_id,
        error,
    )
