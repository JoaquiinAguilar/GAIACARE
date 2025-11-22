# GAIACARE 🌿

A Django-based e-commerce platform for professional care products and equipment.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [User Roles](#user-roles)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

GaiaCare is a comprehensive e-commerce solution built with Django that provides:
- Product catalog management
- Shopping cart functionality
- Order processing and management
- User authentication and profiles
- Admin dashboard with analytics
- Multi-role user system

## ✨ Features

- **Product Management**: Categories, product images, inventory tracking
- **Shopping Cart**: Session-based cart with real-time updates
- **Order System**: Complete order processing workflow
- **User Authentication**: Email-based authentication with django-allauth
- **Dashboard**: Analytics, sales tracking, and administrative tools
- **Responsive Design**: Bootstrap 5 integration
- **File Management**: Static and media files handling with WhiteNoise

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
  ```bash
  python --version
  ```
- **pip** (Python package installer)
  ```bash
  pip --version
  ```
- **virtualenv** (recommended)
  ```bash
  pip install virtualenv
  ```

## 🚀 Installation

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
cd /home/joaquin/Desktop/GaiaCare/GAIACARE
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Navigate to Project Directory

```bash
cd gaiacare/gaia_care
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account. You'll need to provide:
- Email address (used for login)
- Password

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in `/home/joaquin/Desktop/GaiaCare/GAIACARE/gaiacare/gaia_care/` with the following variables:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (if using PostgreSQL instead of SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/gaiacare

# Email Configuration (for production)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-password
```

**Note**: If you don't create a `.env` file, the application will use default development settings.

## 🏃 Running the Project

### Start the Development Server

```bash
# Make sure you're in the directory with manage.py
cd /home/joaquin/Desktop/GaiaCare/GAIACARE/gaiacare/gaia_care

# Run the server
python manage.py runserver
```

The application will be available at:
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### Default Credentials

Use the superuser credentials you created during installation to access the admin panel.

## 📁 Project Structure

```
GAIACARE/
├── gaiacare/
│   └── gaia_care/
│       ├── carts/              # Shopping cart functionality
│       ├── core/               # Core utilities and base templates
│       ├── dashboard/          # Admin dashboard and analytics
│       ├── gaia_care/          # Main project settings
│       │   ├── settings.py     # Django settings
│       │   ├── urls.py         # URL configuration
│       │   └── wsgi.py         # WSGI configuration
│       ├── media/              # User-uploaded files
│       ├── orders/             # Order processing
│       ├── products/           # Product catalog
│       ├── static/             # Static files (CSS, JS, images)
│       ├── staticfiles/        # Collected static files
│       ├── templates/          # HTML templates
│       ├── users/              # User authentication and profiles
│       ├── db.sqlite3          # SQLite database
│       └── manage.py           # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 👥 User Roles

The system supports multiple user roles:

1. **Superuser/Admin**: Full access to all features
2. **Administradores**: Full administrative access
3. **Administradores Limitados**: Limited administrative access
4. **Regular Users**: Shopping and order management

### Creating Admin Groups

After creating your superuser, you can set up admin groups:

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='Administradores')
Group.objects.get_or_create(name='Administradores Limitados')
```

## 🛠️ Development

### Running Migrations After Model Changes

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Sample Data

Access the admin panel at http://127.0.0.1:8000/admin/ to:
- Add product categories
- Create products
- Upload product images
- Manage orders

### Useful Django Commands

```bash
# Create a new app
python manage.py startapp app_name

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check

# View database schema
python manage.py dbshell
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: "Module not found" errors

**Solution**: Make sure your virtual environment is activated and all dependencies are installed:
```bash
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

#### Issue: "No such table" errors

**Solution**: Run migrations:
```bash
python manage.py migrate
```

#### Issue: Static files not loading

**Solution**: Collect static files:
```bash
python manage.py collectstatic --noinput
```

#### Issue: Can't login with username

**Solution**: This project uses **email-based authentication**. Use your email address instead of username.

#### Issue: Email verification required but emails not sending

**Solution**: In development, emails are printed to the console. Check your terminal output for verification links.

### Database Reset (Use with caution!)

If you need to start fresh:
```bash
# Delete the database
rm db.sqlite3

# Delete all migration files (except __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations and database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 📝 Additional Notes

- The project is configured for the **Mexico City timezone** (America/Mexico_City)
- Language is set to **Spanish (es-mx)**
- Uses **SQLite** for development (consider PostgreSQL for production)
- Email backend is set to **console** for development
- Static files are managed with **WhiteNoise** for easy deployment

## 🚀 Production Deployment

For production deployment, consider:
1. Set `DEBUG=False` in your `.env` file
2. Use a production database (PostgreSQL recommended)
3. Configure proper email backend (SMTP)
4. Set up a proper web server (Gunicorn + Nginx)
5. Use environment variables for sensitive data
6. Enable HTTPS
7. Configure proper `ALLOWED_HOSTS`

## 📄 License

This project is proprietary software.

## 🤝 Support

For issues or questions, please contact the development team.

---

**Happy Coding! 🎉**
