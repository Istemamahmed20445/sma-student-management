web: python manage.py collectstatic --noinput && gunicorn student_management.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
