
#!/bin/bash
set -e

echo "Starting deployment process..."

echo "Running migrations..."
python manage.py migrate

echo "Creating admin user..."
python manage.py create_admin

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting server..."
exec gunicorn student_management.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
