from app.core.celery_app import celery_app
from app.tasks.task_handlers import handle_task_failure


@celery_app.task(
    bind=True,
    name="app.tasks.test_tasks.test_task",
)
def test_task(self, message: str = "Celery is working"):
    try:
        print(f"Test task started | id={self.request.id}")

        return {
            "status": "completed",
            "message": message,
            "task_id": self.request.id,
        }

    except Exception as exc:
        handle_task_failure(
            task_name=self.name,
            task_id=self.request.id,
            error=str(exc),
        )

        raise