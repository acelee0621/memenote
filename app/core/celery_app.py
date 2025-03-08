from celery import Celery


celery_app = Celery(
    "memenote",
    broker="amqp://user:bitnami@localhost:5672//",
    backend="redis://localhost:6379/2",
    include=["app.tasks.reminder_task"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    result_expires=3600,
    task_routes={
        "app.tasks.reminder_task.*": {"queue": "reminder_queue"}
    },
)


# uv run celery -A app.core.celery_app worker --loglevel=info --pool=threads -Q celery,reminder_queue --autoscale=4,2