import json
from datetime import datetime


import redis

from app.core.celery_app import celery_app


redis_client = redis.Redis(host="localhost", port=6379, db=0)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@celery_app.task(name="app.tasks.reminder_task.notify_reminder_action")
def notify_reminder_action(message: dict):
    """
    Notify WebSocket clients about a new reminder creation.
    """
    redis_client.publish("reminder_notifications", json.dumps(message, cls=CustomJSONEncoder))
    
    
@celery_app.task(name="app.tasks.reminder_task.trigger_reminder")
def trigger_reminder(reminder_data: dict):
    """
    Handle the triggering of a reminder and update the database asynchronously.
    """
    reminder_data["action"] = "trigger"    
    redis_client.publish("reminder_notifications", json.dumps(reminder_data, cls=CustomJSONEncoder))