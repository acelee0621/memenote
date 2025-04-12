import resend
from app.models.models import User
from app.core.config import settings
from app.core.celery_app import celery_app


resend.api_key = settings.RESEND_API_KEY


@celery_app.task()
def register_email(user: User):
    params: resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": [user.email],
        "subject": "Welcome to MemeNote",
        "html": f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to MemeNote</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #007bff;
                color: white;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                color: white;
                background-color: #007bff;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to MemeNote, {user.full_name}!</h1>
            </div>
            <div class="content">
                <p>Thank you for joining MemeNote! We're excited to have you on board.</p>
                <p>Here are your account details:</p>
                <ul>
                    <li><strong>Username:</strong> {user.username}</li>
                    <li><strong>Email:</strong> {user.email}</li>
                </ul>
                <p>Get started by exploring our platform and creating your first meme note!</p>
                <a href="https://your-memenote-url.com" class="button">Explore MemeNote</a>
            </div>
            <div class="footer">
                <p>&copy; 2023 MemeNote. All rights reserved.</p>
                <p>If you have any questions, contact us at support@memenote.com.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    }
    resend.Emails.send(params)
