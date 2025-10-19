#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify Django installation
echo "Verifying Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Initialize currencies
echo "Initializing currencies..."
python manage.py init_currencies

# Create superuser if it doesn't exist
echo "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Verify gunicorn installation
echo "Verifying gunicorn installation..."
python -c "import gunicorn; print(f'Gunicorn version: {gunicorn.__version__}')"

echo "Build completed successfully!"
