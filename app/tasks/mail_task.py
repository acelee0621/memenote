import resend

from app.core.config import settings
from app.core.celery_app import celery_app


resend.api_key = settings.RESEND_API_KEY


@celery_app.task()
def register_email(user_data: dict):
    params: resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": [user_data["email"]],
        "subject": "Welcome to MemeNote",
        "html": f"""    
        <div>
            <div>
                <h1>Welcome to MemeNote, {user_data["full_name"]}!</h1>
            </div>
            <div>
                <p>Thank you for joining MemeNote! We're excited to have you on board.</p>
                <p>Here are your account details:</p>
                <ul>
                    <li><strong>Username:</strong> {user_data["username"]}</li>
                    <li><strong>Email:</strong> {user_data["email"]}</li>
                </ul>
                <p>Get started by exploring our platform and creating your first meme note!</p>
                <a href="https://your-memenote-url.com" class="button">Explore MemeNote</a>
            </div>
            <div>
                <p>&copy; 2023 MemeNote. All rights reserved.</p>
                <p>If you have any questions, contact us at support@memenote.com.</p>
            </div>
        </div>    
    """,
    }
    resend.Emails.send(params)
