[中文文档](https://github.com/acelee0621/memenote/blob/main/README_zh.md)

# Memenote Project 📝✨

Welcome to **Memenote**! This is a FastAPI-based note-taking tool designed for recording and managing your inspirations and tasks. It uses `uv` for dependency management and supports user registration, note creation, To-dos, Reminders, and real-time reminders powered by Celery, delivered to your client via SSE (Server-Sent Events)! 📩 **New Feature: Supports note attachment upload, download, and sharing, integrated with MinIO (or S3 compatible storage) using Boto3.** 📎 The project uses Alembic for database migrations and is Dockerized, supporting development mode and production configuration with Traefik for HTTPS. Come give it a try! 🚀

---

## Project Overview 🌟

Memenote is a lightweight yet powerful note management tool designed to help you:
- 📋 Create and manage personal notes (Note)
- 📎 **Add attachments to notes**: Supports file upload, download, and generating sharing links via MinIO (S3 compatible)
- ✅ Add To-dos under notes or create standalone To-dos
- ⏰ Set Reminders, which can be associated with notes or exist independently
- 🔒 User registration and authentication to ensure data security
- 📡 Real-time reminder push notifications via Celery and SSE
- 🐳 Docker deployment, supporting both development and production environments

Whether you want to capture ideas, plan tasks, set timed reminders, or **add attachments to your notes**, Memenote can help you out! 💪

---

## Quick Start 🚀

Memenote uses `uv` for managing dependencies and the runtime environment. If you haven't used `uv` before, don't worry! Here are the detailed steps to get you up and running~ 😎

### 1. Prerequisites ⚙️
- **Python Version**: 3.8+
- **Install uv**:
  Run in terminal:
  ```bash
  pip install uv
  ```
  Or refer to the [uv official documentation](https://github.com/astral-sh/uv).
- **MinIO (or S3 Compatible Service)**: You need a running MinIO instance or a configured S3 compatible object storage service for attachment storage.

### 2. Clone Project 📥
Get the code locally:
```bash
git clone https://github.com/acelee0621/memenote.git
cd memenote
```

### 3. Install Dependencies with uv 📦
Dependencies are defined in `pyproject.toml`. Install quickly using `uv` (includes `boto3`):
```bash
uv sync
```

### 4. Configure Environment Variables 🌍
Copy `.env.example` to `.env` and modify as needed:
```bash
cp .env.example .env
```
- `JWT_SECRET`: Secret key for user authentication
- `JWT_ALGORITHM`: JWT encryption algorithm (`HS256`)
- `BROKER_HOST` and `REDIS_HOST`: Message queue and result backend addresses for Celery (optional, default `localhost`)
- `POSTGRES_HOST`: Database host (optional, default `localhost`)
- `POSTGRES_PORT`: Database port (optional, default `5432`)
- `POSTGRES_DB`: Database name (optional, default `memenote`)
- `POSTGRES_USER`: Database username (optional, default `postgres`)
- `POSTGRES_PASSWORD`: Database password (optional, default `postgres`)
- **`MINIO_ENDPOINT`**: MinIO service address (e.g., `localhost:9000`)
- **`MINIO_ACCESS_KEY`**: MinIO access key
- **`MINIO_SECRET_KEY`**: MinIO secret key
- **`MINIO_BUCKET_NAME`**: Bucket name for storing attachments (e.g., `memenote-attachments`)
- **`MINIO_USE_SSL`**: Whether to use SSL for MinIO connection (`True` or `False`, default `False`)

### 5. Run Database Migrations 🗄️
Initialize the database schema:
```bash
uv run alembic upgrade head
```

### 6. Start FastAPI Service ▶️
Run the main application:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` to view the API documentation! 📖

### 7. Start Celery Worker 🕒
The reminder feature depends on Celery. Run in a separate terminal:
```bash
uv run celery -A app.core.celery_app worker --loglevel=info --pool=threads -Q celery,reminder_queue --autoscale=4,2
```

---

## Docker Deployment 🐳

Want to run it with Docker? We provide three configurations:

**Note**: The following Docker configurations do not include the MinIO service by default. You need to run a MinIO instance yourself and provide the correct connection details in the `.env` file or Docker Compose configuration.

### Development Mode 🛠️
```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --watch
```
- Includes FastAPI, Celery Worker, and Redis, suitable for local development.

### Production Mode (No HTTPS)
```bash
docker compose up -d
```

### Production Mode + HTTPS 🔐
Using Traefik for HTTPS:
```bash
docker compose -f compose.traefik.yaml up -d
```
- Requires `cert.pem` and `key.pem` under `traefik/certs/`.
- Listens on port `443` by default, ensure certificate configuration is correct.

---

## Project Structure 🗂️
Quickly understand the code layout:
```
memenote/
├── app/                 # Main application directory
│   ├── core/            # Core configurations (Database, Celery, Auth, S3 Client, etc.)
│   ├── models/          # Data models (User, Note, Todo, Reminder, Attachment, etc.)
│   ├── repository/      # Data access layer
│   ├── routes/          # API routes (Auth, Notes, Reminders, Attachments, etc.)
│   ├── schemas/         # Data validation schemas
│   ├── service/         # Business logic layer.
│   ├── tasks/           # Celery tasks
│   └── main.py          # FastAPI entry point
├── alembic/             # Database migrations
├── tests/               # Test cases
├── traefik/             # Traefik configuration (production)
├── Dockerfile           # Docker image definition
├── compose.yaml         # Base Docker Compose configuration
├── compose.dev.yaml     # Development Docker Compose configuration
├── compose.traefik.yaml # Traefik Docker Compose configuration
├── .env.example         # Example environment variables
├── pyproject.toml       # uv dependency management file
└── README.md            # The document you are reading! 😊
```


---

## Feature Highlights 🌈
- **User Management** 👤: Register, login, JWT authentication protects your data.
- **Note System** 📝: Create, edit, delete notes. Each note can be associated with To-dos and Reminders.
- **Attachment Management** 📎: Add attachments to notes, supporting upload, download, and generating sharing links via MinIO (S3 compatible).
- **To-do Items** ✅: Supports standalone or note-associated To-dos, with completion status tracking.
- **Reminder Function** ⏰: Set reminder times, Celery scheduled tasks push notifications in real-time via SSE.
- **Real-time Notifications** 📡: Receive reminders using Server-Sent Events (SSE).
- **Docker Support** 🐳: One-click deployment, covering both development and production environments!

---

## Important Notes ⚠️
- **Database**: Uses PostgreSQL by default.
- **Object Storage**: **Requires a running MinIO instance or configured S3 compatible service. Connection details must be correctly set in the `.env` file. Ensure the specified Bucket exists.**
- **Celery**: Ensure Redis and RabbitMQ (or an alternative broker) are running correctly.
- **HTTPS**: Requires Traefik and certificate configuration for production environments.
- **Feedback**: Encountered an issue? Please file an issue, I'll respond as soon as possible! ✨

---

## Contributing 🤝
Like Memenote and want to add something? Contributions are welcome:
1. Fork the project
2. Create a branch (`git checkout -b feature/cool-idea`)
3. Commit your changes (`git commit -m "✨ Add awesome feature"`)
4. Push to the branch (`git push origin feature/cool-idea`)
5. Create a Pull Request

---

## Contact Me 📬
Have questions or suggestions? Feel free to open an issue on GitHub.
Let's make Memenote even better together! 🌟

---

## Acknowledgements 🙏
Thanks to FastAPI, Celery, uv, Boto3, MinIO, and the entire open-source community for their support! And thank you for using Memenote! 💖

---

## Acknowledgments

- Inspired by [Memos](https://github.com/usememos/memos).