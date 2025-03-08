from celery import Celery



celery_app = Celery(
    "memenote",
    broker="amqp://user:bitnami@localhost:5672//",
    backend="redis://localhost:6379/2"
)

celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"


from app.tasks.reminder import notify_reminder_creation
# celery_app.autodiscover_tasks(['app.tasks'])


