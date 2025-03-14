import os

from celery import Celery


broker_host = os.getenv("BROKER_HOST", "localhost:5672")
CELERY_BROKER_URL = f"amqp://user:bitnami@{broker_host}//"

redis_host = os.getenv("REDIS_HOST", "localhost:6379")
CELERY_RESULT_BACKEND = f"redis://{redis_host}/2"


celery_app = Celery(
    "memenote",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.reminder_task"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    result_expires=3600,
    task_routes={"app.tasks.reminder_task.*": {"queue": "reminder_queue"}},
)


# uv run celery -A app.core.celery_app worker --loglevel=info --pool=threads -Q celery,reminder_queue --autoscale=4,2
