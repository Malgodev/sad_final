# Healthcare Management System

A Django-based healthcare management system with modules for doctors, patients, appointments, and AI-powered self-testing.

## Features

- **Doctor Portal**: Doctor registration, profiles, and dashboard
- **Patient Portal**: Patient registration, profiles, and appointment management
- **Appointment System**: Booking and management of medical appointments
- **Self Test System**: AI-powered symptom analysis and health recommendations

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd healthcare-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Navigate to the Django project directory:
```bash
cd src/healthcare
```

4. Create and apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (admin account):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Open your browser and visit:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
src/healthcare/
├── healthcare/          # Main project settings
├── doctor/             # Doctor management app
├── patient/            # Patient management app
├── appointment/        # Appointment booking app
├── selftest/           # AI self-testing app
└── manage.py           # Django management script
```

## Available URLs

- `/` - Home page with navigation links
- `/admin/` - Django admin panel
- `/doctor/` - Doctor portal
- `/patient/` - Patient portal
- `/appointment/` - Appointment management
- `/selftest/` - Self-test system

## Database

The project uses SQLite as the default database, which will be created automatically when you run migrations.

## Development

To add new features or modify existing ones:

1. Make changes to the relevant app
2. Create migrations if you modify models:
```bash
python manage.py makemigrations
```
3. Apply migrations:
```bash
python manage.py migrate
```
4. Test your changes by running the server

## Next Steps

This is a basic "Hello World" version. Future enhancements could include:

- User authentication and registration forms
- Appointment booking forms
- AI integration for self-testing
- Email notifications
- API endpoints for mobile apps
- Advanced reporting and analytics 