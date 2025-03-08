from app.core.celery_app import celery_app
import redis
import json
from datetime import datetime

redis_client = redis.Redis(host="localhost", port=6379, db=0)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@celery_app.task
def notify_reminder_action(message: dict):
    """
    Notify WebSocket clients about a new reminder creation.
    """
    redis_client.publish("reminder_notifications", json.dumps(message, cls=CustomJSONEncoder))