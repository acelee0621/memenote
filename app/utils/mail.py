from typing import Optional

import resend
from fastapi import BackgroundTasks
from app.models.models import User




resend.api_key = "re_VJRjDCxS_LvYvzKV1a5RjXUGjJmTbBuwn"


       
        
def send_register_email(
    user: User,    
    background_tasks: Optional[BackgroundTasks] = None
):    
    params: resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": [user.email],
        "subject": "Verify your email",
        "html": f"""
            <h1>Welcome to MemeNote {user.full_name}</h1>
            <p>Thank you for registering</p>
            <p>Username: {user.username}</p>
            <p>Email: {user.email}</p>
            
        """,
    }
    # 如果有后台任务，使用后台发送
    if background_tasks:
        background_tasks.add_task(resend.Emails.send, params)
    else:
        resend.Emails.send(params)