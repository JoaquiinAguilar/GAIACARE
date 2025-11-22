#!/bin/bash

# GaiaCare Setup Script
# This script automates the setup process for the GaiaCare Django project

echo "🌿 GaiaCare Setup Script"
echo "========================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo ""

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully"
echo ""

# Navigate to project directory
cd gaiacare/gaia_care

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

echo ""
echo "✅ Database migrations completed"
echo ""

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Static files collected"
echo ""

# Prompt for superuser creation
echo "👤 Would you like to create a superuser now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the development server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Navigate to project: cd gaiacare/gaia_care"
echo "  3. Run server: python manage.py runserver"
echo ""
echo "Access the application at: http://127.0.0.1:8000/"
echo "Access the admin panel at: http://127.0.0.1:8000/admin/"
echo ""
