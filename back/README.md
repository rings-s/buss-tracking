# Bus Tracking System - Backend

Django-based REST API for bus tracking and employee attendance management.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ 
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   cd /path/to/buss-tracking/back
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # Development dependencies (optional but recommended)
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and update SECRET_KEY and other settings
   nano .env  # or use your preferred editor
   ```

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

---

## 📚 Project Structure

```
back/
├── accounts/          # User authentication & management
├── base/              # Core models (Bus, Trip, Route, etc.)
├── back/              # Django project settings
├── manage.py          # Django management script
├── requirements.txt   # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── .env               # Environment variables (not in git)
└── API_ENDPOINTS.md   # API documentation
```

---

## 🔑 Key Features

- **JWT Authentication**: Secure token-based authentication
- **User Roles**: Admin, Driver, Employee
- **Real-time Bus Tracking**: GPS location updates
- **NFC Check-in**: Employee attendance via NFC
- **Trip Management**: Start/end trips with route tracking
- **Admin Dashboard**: Statistics and reporting

---

## 📖 API Documentation

See [API_ENDPOINTS.md](./API_ENDPOINTS.md) for complete API documentation.

### Key Endpoints

- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/
- **Authentication**: http://localhost:8000/api/auth/login/
- **Dashboard**: http://localhost:8000/api/dashboard/

---

## 🧪 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8
```

### Create New Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Shell (with IPython)
```bash
python manage.py shell
# or with django-extensions:
python manage.py shell_plus
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Database

Default: SQLite3 (`db.sqlite3`)  
For production: Configure PostgreSQL in settings.py

---

## 📦 Dependencies

### Production
- Django 5.2
- Django REST Framework
- dj-rest-auth (JWT authentication)
- django-allauth (Social authentication)
- django-cors-headers (CORS support)
- python-dotenv (Environment variables)

### Development (Optional)
- django-debug-toolbar (Debug queries)
- pytest-django (Testing)
- black (Code formatting)
- flake8 (Linting)

---

## 🔐 Security Notes

- Never commit `.env` to version control
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS` in production
- Use HTTPS in production

---

## 📝 Common Commands

```bash
# Run development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Run tests
pytest

# Check for issues
python manage.py check
```

---

## 🤝 Contributing

1. Create a new branch for your feature
2. Write tests for new functionality
3. Format code with `black` and `isort`
4. Ensure tests pass with `pytest`
5. Submit a pull request

---

## 📄 License

[Add your license here]

---

## 🆘 Troubleshooting

### ImportError: No module named 'django'
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration conflicts
```bash
# Reset migrations (DEV ONLY - DESTROYS DATA)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### CORS errors
Check `CORS_ALLOWED_ORIGINS` in `.env` matches your frontend URL.

---

## 📬 Support

For issues and questions, please open an issue on GitHub or contact the development team.
