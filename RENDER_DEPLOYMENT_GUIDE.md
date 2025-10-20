# Render Deployment Guide with PostgreSQL

## Your Render PostgreSQL Database Details
- **Hostname**: dpg-d3r5fh8dl3ps73ce5lj0-a.oregon-postgres.render.com
- **Port**: 5432
- **Database**: student_management_db_wkuv
- **Username**: student_management_db_wkuv_user
- **Password**: xiNTvRXZi4wRRLVPUguDzBQG6Q06sN4k
- **External URL**: postgresql://student_management_db_wkuv_user:xiNTvRXZi4wRRLVPUguDzBQG6Q06sN4k@dpg-d3r5fh8dl3ps73ce5lj0-a.oregon-postgres.render.com/student_management_db_wkuv

## Steps to Deploy on Render

### 1. Create Web Service on Render
1. Go to [render.com](https://render.com) dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your Django project repository

### 2. Configure Build Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn student_management.wsgi:application`

### 3. Set Environment Variables
In Render dashboard, add these environment variables:

```
SECRET_KEY=django-insecure-%7)!f&f&(q%-22a0x+_clq7n1j0$*d75=nev53$xkyghx(12vh
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DB_NAME=student_management_db_wkuv
DB_USER=student_management_db_wkuv_user
DB_PASSWORD=xiNTvRXZi4wRRLVPUguDzBQG6Q06sN4k
DB_HOST=dpg-d3r5fh8dl3ps73ce5lj0-a.oregon-postgres.render.com
DB_PORT=5432
USE_SQLITE=False
```

### 4. Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Start your application

### 5. Access Your Application
- Your app will be available at: `https://your-app-name.onrender.com`
- Admin panel: `https://your-app-name.onrender.com/admin/`
- Login with: username: `admin`, password: `admin123`

## Features Included
✅ PostgreSQL database integration
✅ All existing features preserved
✅ Firebase integration maintained
✅ PWA support
✅ Student management
✅ Batch management
✅ Fee management
✅ Contact management
✅ User authentication

## Database Status
✅ All migrations applied successfully
✅ Superuser created
✅ Database connection tested
✅ Ready for production deployment

## Troubleshooting
- If deployment fails, check the build logs in Render dashboard
- Ensure all environment variables are set correctly
- Database migrations run automatically during deployment
- Static files are served by WhiteNoise middleware