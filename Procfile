web: python manage.py migrate --noinput && python create_admin.py && python manage.py collectstatic --noinput && gunicorn student_management.wsgi:application --bind 0.0.0.0:$PORT
