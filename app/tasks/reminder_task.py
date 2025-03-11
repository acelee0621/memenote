import json
from datetime import datetime

import redis

from app.core.celery_app import celery_app


redis_client = redis.from_url(
    "redis://localhost:6379/0",
    health_check_interval=30,
)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@celery_app.task(name="app.tasks.reminder_task.notify_reminder_action")
def notify_reminder_action(message: dict):
    # user_id = message["user_id"]
    # channel = f"reminder_notifications_{user_id}"
    channel = "reminder_notifications"
    print(f"Publishing to {channel}: {message}")
    message_json = json.dumps(message, cls=CustomJSONEncoder)
    # 发布到 Pub/Sub 频道
    redis_client.publish(channel, message_json)


@celery_app.task(name="app.tasks.reminder_task.trigger_reminder")
def trigger_reminder(reminder_data: dict):
    reminder_data["action"] = "trigger"
    # user_id = reminder_data["user_id"]
    # channel = f"reminder_notifications_{user_id}"
    channel = "reminder_notifications"
    print(f"Publishing to {channel}: {reminder_data}")
    message_json = json.dumps(reminder_data, cls=CustomJSONEncoder)
    # 发布到 Pub/Sub 频道
    redis_client.publish(channel, message_json)
