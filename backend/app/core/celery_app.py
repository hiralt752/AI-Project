"""Provide celery app components for the application."""

import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "amqp://ai_project:ai_project_password@localhost:5672//",
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0",
)


celery_app = Celery(
    "ai_project",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.test_tasks",
        "app.tasks.image_tasks",
        "app.tasks.document_tasks",
    ],
)


# --------------------------------------------------
# General Celery configuration
# --------------------------------------------------

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="Asia/Kolkata",
    enable_utc=True,

    task_track_started=True,

    # Retry configuration
    task_default_retry_delay=10,
    task_max_retries=3,

    # Timeout configuration
    task_soft_time_limit=600,
    task_time_limit=720,

    # Queue configuration
    task_default_queue="default",

    # Prevent tasks from being prefetched unnecessarily
    worker_prefetch_multiplier=1,

    # Don't acknowledge a task until it finishes
    task_acks_late=True,
)


# --------------------------------------------------
# Task routing
# --------------------------------------------------

celery_app.conf.task_routes = {
    "app.tasks.image_tasks.*": {
        "queue": "image_queue",
    },

    "app.tasks.document_tasks.*": {
        "queue": "document_queue",
    },

    "app.tasks.test_tasks.*": {
        "queue": "default",
    },
}


# --------------------------------------------------
# Queue declarations
# --------------------------------------------------

celery_app.conf.task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    },

    "image_queue": {
        "exchange": "image",
        "routing_key": "image",
    },

    "document_queue": {
        "exchange": "document",
        "routing_key": "document",
    },
}
