# =============================================================================
# app/celery_app.py  --  Celery : durable distributed background tasks (ADVANCED)
# =============================================================================
# WHY CELERY when FastAPI already has BackgroundTasks?
#   * FastAPI BackgroundTasks = in-process, fire-and-forget, lost if the worker
#     crashes, cannot retry, cannot scale beyond one process.
#   * Celery = a distributed task QUEUE backed by a broker (Redis):
#       - durable     : tasks are persisted; workers pick them up
#       - retryable   : automatic retries on failure
#       - scalable    : run many worker processes/machines
#       - scheduled   : periodic tasks (beat), e.g. daily cleanup
#   This is THE production answer to background/async processing.
#
# RUN IT:
#   .venv/bin/celery -A app.celery_app.celery worker --loglevel=info
#   (from the src/ directory)

from celery import Celery

from app.core.config import settings

# broker= where tasks are queued (Redis), backend=where results are stored.
celery = Celery(
    "taskflow",
    broker=settings.REDIS_URL,        # tasks sit here until a worker takes one
    backend=settings.REDIS_URL,       # task results/status stored here
)

# Normalize config (task serialization = JSON, timezone = UTC).
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # How many times to retry a task that raises an exception.
    task_default_retry_delay=5,
    task_max_retries=3,
)


# --- A task ----------------------------------------------------------------
# @celery.task turns a function into a distributable task. Call it with
# `send_task.apply_async(args=[...])` or just `send_task.delay(...)`.
@celery.task(name="tasks.send_report_email")
def send_report_email(user_email: str, report_id: int) -> dict:
    """Simulate a long-running, durable background job (sending an email).
       celery will call this on a worker (not in the request thread)."""
    # In a real app: SMTP call, or build a PDF, upload to S3, etc.
    print(f"[celery] Sending report {report_id} to {user_email}")
    return {"email": user_email, "report_id": report_id, "status": "sent"}


# --- Schedule a recurring task (optional, uncomment to use) -----------------
celery.conf.beat_schedule = {
    # Every 30 minutes, run the cleanup task "so_called" below.
    # Requires running: `celery -A app.celery_app.celery beat`
}
