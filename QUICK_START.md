# Django Todo List - Quick Start Guide

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation & Setup

### Option 1: Automatic Setup (Recommended)

On **Windows**, simply double-click:
```
setup.bat
```

On **macOS/Linux**:
```bash
python setup.py
```

Or run it manually:
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file (if not already created):**
   ```bash
   cp .env.example .env
   ```
   Or create `.env` manually with the provided content.

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser (optional but recommended):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Collect static files (optional for development):**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Running the Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - Create new user
- `POST /api/auth/login/` - Login user

### Todos (requires authentication)
- `GET /api/todos/` - List all todos
- `POST /api/todos/` - Create a new todo
- `GET /api/todos/{id}/` - Get specific todo
- `PUT /api/todos/{id}/` - Update todo
- `PATCH /api/todos/{id}/` - Partial update todo
- `DELETE /api/todos/{id}/` - Delete todo
- `GET /api/todos/stats/` - Get todo statistics

## Project Structure

```
├── apps/
│   └── todos/              # Todo app with models, views, serializers
│       ├── migrations/     # Database migrations
│       ├── models.py       # Todo model
│       ├── views.py        # API views (Signup, Login, TodoViewSet)
│       ├── serializers.py  # DRF serializers
│       └── urls.py         # URL routing for todos app
├── authentication/         # JWT authentication backend
│       └── jwt_auth.py     # Custom JWT authentication class
├── config/                 # Django configuration
│       ├── settings.py     # Django settings
│       ├── urls.py         # Main URL configuration
│       ├── wsgi.py         # WSGI application
│       └── asgi.py         # ASGI application
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (don't commit!)
└── README.md             # This file
```

## Features

- ✅ User authentication with DRF Token Authentication
- ✅ JWT token support for API
- ✅ Todo CRUD operations with filtering
- ✅ User-specific todo isolation
- ✅ REST API endpoints
- ✅ Django admin panel
- ✅ Bootstrap UI (coming soon)

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
- Run: `pip install -r requirements.txt`

### "Module not found" errors
- Ensure you're in the project root directory
- Verify virtual environment is activated (if using one)
- Run: `python manage.py check`

### Database issues
- Delete `db.sqlite3` and run: `python manage.py migrate`
- This will reset the database to a clean state

### Port 8000 already in use
- Use a different port: `python manage.py runserver 8001`

## Testing

Run the test suite:
```bash
python manage.py test
```

## Environment Variables

Key variables in `.env`:
- `DEBUG=1` - Enable debug mode (set to `0` for production)
- `DJANGO_SECRET_KEY` - Secret key for Django
- `JWT_SECRET` - Secret key for JWT tokens
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

## Development Commands

```bash
# Show all available commands
python manage.py help

# Create new app
python manage.py startapp <app_name>

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Run tests
python manage.py test

# Clear database (reset to initial state)
python manage.py flush
```

## Security Notes

⚠️ **Important for Production:**
- Never commit `.env` file
- Change `DJANGO_SECRET_KEY` and `JWT_SECRET`
- Set `DEBUG=0`
- Set `ALLOWED_HOSTS` appropriately
- Use HTTPS in production
- Implement proper CORS settings

## License

This project is part of the AI Dev Team initiative.

## Support

For issues or questions, please refer to the documentation or create an issue.
