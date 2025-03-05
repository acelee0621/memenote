# Memenote

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Memenote** is a lightweight, open-source note-taking application inspired by [Memos](https://github.com/usememos/memos). It allows users to quickly jot down short notes, excerpts, or ideas, and optionally attach todos and reminders to them. Designed for simplicity and efficiency, Memenote provides a clean RESTful API backend built with modern Python technologies.

## Features

- **Notes**: Create, update, and delete short notes with optional titles and content.
- **Todos**: Add standalone or note-associated todo items with completion tracking.
- **Reminders**: Set reminders linked to notes or todos, with triggered and acknowledged states.
- **User Management**: Basic user authentication (to be implemented).
- **Asynchronous Backend**: Powered by FastAPI and SQLAlchemy 2.0 for efficient async database operations.
- **Data Isolation**: Each user's data (notes, todos, reminders) is isolated via `user_id`.

Planned future enhancements:
- Real-time notifications using RabbitMQ and WebSocket.
- Scheduled reminders with Celery tasks.
- Frontend interface mimicking Memos' simplicity.

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (v0.115.0 or latest)
- **Database ORM**: [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) with async support (`asyncio`)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Python**: 3.13 (latest syntax, e.g., `str | None`)
- **Database**: SQLite (development), PostgreSQL (production-ready)

## Project Structure

```
memenote/
├── main.py          # FastAPI application entry point
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic schemas for request/response validation
├── README.md        # Project documentation (this file)
└── requirements.txt # Dependencies
```

## Installation

### Prerequisites
- Python 3.13+
- pip (Python package manager)

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/acelee0621/memenote.git
   cd memenote
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## API Endpoints

### Notes
- `POST /notes`: Create a new note.
- `GET /notes`: List all notes with associated todos and reminders.
- `GET /notes/{note_id}`: Retrieve a single note with its todos and reminders.
- `PATCH /notes/{note_id}`: Update a note.
- `DELETE /notes/{note_id}`: Delete a note.

### Todos
- `POST /todos`: Create a todo (standalone or linked to a note via `note_id`).
- `GET /todos`: List all todos.
- `GET /todos?note_id={note_id}`: Filter todos by note.
- `GET /todos/{todo_id}`: Retrieve a single todo.
- `PATCH /todos/{todo_id}`: Update a todo (e.g., mark as completed).
- `DELETE /todos/{todo_id}`: Delete a todo.

### Reminders
- `POST /reminders`: Create a reminder (standalone or linked to a note/todo via `note_id`/`todo_id`).
- `GET /reminders`: List all reminders.
- `GET /reminders?note_id={note_id}`: Filter reminders by note.
- `GET /reminders?todo_id={todo_id}`: Filter reminders by todo.
- `GET /reminders/{reminder_id}`: Retrieve a single reminder.
- `PATCH /reminders/{reminder_id}`: Update a reminder (e.g., mark as acknowledged).
- `DELETE /reminders/{reminder_id}`: Delete a reminder.

## Database Models

### User
- `id`: Integer (Primary Key)
- `username`: String (Unique, Required)
- `password_hash`: String (Required)
- `email`: String | None
- `created_at`: DateTime
- Relationships: `notes`, `todos`, `reminders`

### Note
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `title`: String | None
- `content`: String | None
- `created_at`: DateTime
- `updated_at`: DateTime
- Relationships: `user`, `todos`, `reminders`

### Todo
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `note_id`: Integer | None (Foreign Key)
- `content`: String (Required)
- `is_completed`: Boolean (Default: False)
- `created_at`: DateTime
- `updated_at`: DateTime
- Relationships: `user`, `note`

### Reminder
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `note_id`: Integer | None (Foreign Key)
- `todo_id`: Integer | None (Foreign Key)
- `reminder_time`: DateTime (Required)
- `message`: String | None
- `is_triggered`: Boolean (Default: False)
- `is_acknowledged`: Boolean (Default: False)
- `created_at`: DateTime
- Relationships: `user`, `note`, `todo`

## Development Status

- [x] Database models and Pydantic schemas defined.
- [x] User authentication (JWT).
- [x] Basic CRUD API endpoints implemented.
- [ ] Reminder scheduling with Celery.
- [ ] Notification system with RabbitMQ and WebSocket.
- [ ] Frontend development.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Inspired by [Memos](https://github.com/usememos/memos).