# Railway Deployment Guide for SMA Student Management System

## 🚀 Quick Setup Steps

### 1. Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `sma-student-management` repository
5. Railway will automatically detect Django and start deploying!

### 2. Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable

### 3. Configure Environment Variables
In Railway dashboard → Variables tab, add these variables:

#### Required Variables:
```
SECRET_KEY=django-insecure-%7)!f&f&(q%-22a0x+_clq7n1j0$*d75=nev53$xkyghx(12vh
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,*.railway.app,*.up.railway.app
```

#### PWA Configuration:
```
PWA_APP_NAME=SMA Student Management
PWA_APP_DESCRIPTION=Student Management System with PWA support
PWA_APP_THEME_COLOR=#3B82F6
PWA_APP_BACKGROUND_COLOR=#FFFFFF
PWA_APP_DISPLAY=standalone
PWA_APP_SCOPE=/
PWA_APP_ORIENTATION=portrait
PWA_APP_START_URL=/
PWA_APP_STATUS_BAR_STYLE=default
```

#### Security Settings:
```
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Application Settings:
```
APP_NAME=SMA Student Management System
APP_VERSION=1.0.0
APP_ENVIRONMENT=production
TIME_ZONE=UTC
LANGUAGE_CODE=en-us
LOG_LEVEL=INFO
```

### 4. Update ALLOWED_HOSTS
After deployment, Railway will give you a URL like:
`https://sma-student-management-production-xxxx.up.railway.app`

Update the `ALLOWED_HOSTS` variable to include your specific Railway URL:
```
ALLOWED_HOSTS=localhost,127.0.0.1,*.railway.app,*.up.railway.app,sma-student-management-production-xxxx.up.railway.app
```

### 5. Create Superuser
After deployment, you'll need to create an admin user:
1. Go to Railway dashboard → Deployments
2. Click on your deployment
3. Go to "Logs" tab
4. Click "Open Shell"
5. Run: `python manage.py createsuperuser`

### 6. Test PWA Installation
Once deployed, your app will be available at your Railway URL with HTTPS:
- ✅ **HTTPS**: Automatically provided by Railway
- ✅ **Service Worker**: Will work with HTTPS
- ✅ **Manifest**: Already configured
- ✅ **Icons**: Already uploaded
- ✅ **Install Prompts**: Will work on all devices!

## 📱 PWA Testing

### Desktop Testing:
1. Open your Railway URL in Chrome/Edge
2. Look for install icon (⬇️) in address bar
3. Click to install the PWA

### Mobile Testing:
1. Open your Railway URL on mobile
2. Look for "Add to Home Screen" prompt
3. Or use browser menu → "Add to Home Screen"

## 🔧 Troubleshooting

### Common Issues:
1. **500 Error**: Check logs in Railway dashboard
2. **Static Files Not Loading**: Ensure `STATIC_ROOT` is set correctly
3. **Database Error**: Verify PostgreSQL is added and `DATABASE_URL` is set
4. **PWA Not Installing**: Ensure HTTPS is working (Railway provides this automatically)

### Useful Commands:
```bash
# Check deployment logs
railway logs

# Open shell in Railway
railway shell

# Run Django commands
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 🎯 Expected Results

After successful deployment:
- ✅ App accessible via HTTPS URL
- ✅ PWA install prompts working
- ✅ All features functional
- ✅ Database connected
- ✅ Static files served correctly

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify all environment variables are set
3. Ensure PostgreSQL database is connected
4. Test PWA installation on different devices

Your SMA Student Management System will be live and ready for PWA installation! 🎉
