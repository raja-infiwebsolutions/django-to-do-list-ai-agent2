# Django Todo Backend

This repository contains a Django REST Framework backend for a Todo application with user authentication, todo CRUD operations, and a modern REST API.

## Quick Start

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

### TL;DR - Quick Setup

**Windows:**
```batch
setup.bat
python manage.py runserver
```

**macOS/Linux:**
```bash
python setup.py
python manage.py runserver
```

## Features

- User signup/login using DRF Token Authentication + JWT
- Todo model with CRUD operations via REST API
- Viewset-based API endpoints
- User-isolated todos (each user sees only their todos)
- Django admin panel integration
- Bootstrap-based frontend templates

## Tech Stack

- Django 4.2
- Django REST Framework
- JWT (PyJWT)
- SQLite (development)
- Bootstrap 5 (frontend)

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login

### Todos
- `GET /api/todos/` - List todos
- `POST /api/todos/` - Create todo
- `GET /api/todos/{id}/` - Get todo
- `PUT /api/todos/{id}/` - Update todo
- `PATCH /api/todos/{id}/` - Partial update
- `DELETE /api/todos/{id}/` - Delete todo
- `GET /api/todos/stats/` - Get statistics

## Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Start server: `python manage.py runserver`

Access the app at `http://localhost:8000`

## Project Structure

```
apps/todos/              # Todo application
authentication/          # JWT authentication
config/                  # Django configuration
templates/               # HTML templates
static/                  # CSS, JS, images
manage.py               # Django CLI
requirements.txt        # Python dependencies
```

## Documentation

- Full setup guide: [QUICK_START.md](QUICK_START.md)
- API documentation: See [QUICK_START.md](QUICK_START.md#api-endpoints)
- Project structure: [QUICK_START.md](QUICK_START.md#project-structure)

## License

This project is part of the AI Dev Team initiative.

