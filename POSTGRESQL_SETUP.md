# PostgreSQL Setup Guide for Student Management System

## Prerequisites
1. PostgreSQL installed on your system
2. Python virtual environment activated
3. psycopg2-binary installed

## Step 1: Install PostgreSQL (macOS)
```bash
brew install postgresql
brew services start postgresql
```

## Step 2: Create Database and User
```bash
sudo -u postgres psql
```

Run these SQL commands:
```sql
CREATE DATABASE student_management_db;
CREATE USER student_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE student_management_db TO student_user;
ALTER USER student_user CREATEDB;
\q
```

## Step 3: Create Environment File
Create a `.env` file in your project root with:
```
SECRET_KEY=django-insecure-%7)!f&f&(q%-22a0x+_clq7n1j0$*d75=nev53$xkyghx(12vh
DEBUG=True
DB_NAME=student_management_db
DB_USER=student_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
USE_SQLITE=False
```

## Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Step 5: Test Connection
```bash
python manage.py runserver
```

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running: `brew services list | grep postgresql`
- Check if database exists: `psql -U student_user -d student_management_db`
- Verify credentials in `.env` file

### Migration Issues
- If migrations fail, try: `python manage.py migrate --run-syncdb`
- Reset migrations: `python manage.py migrate --fake-initial`

### Fallback to SQLite
If PostgreSQL doesn't work, set `USE_SQLITE=True` in your `.env` file.

## Production Deployment
For production (Render/Railway), they will automatically provide:
- `DATABASE_URL` environment variable
- PostgreSQL database instance
- Connection pooling

Your Django settings are already configured to use these automatically.
