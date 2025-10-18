# 🔧 Render Environment Variables - Complete List

# ===========================================
# REQUIRED VARIABLES (Must Set These)
# ===========================================

# Django Core Settings
DEBUG=False
SECRET_KEY=v+@5rt&lx)tw4#e&4-+!-0a_z905rjp998i9ovpp^kpyg*7rxk

# ===========================================
# OPTIONAL VARIABLES (Set If Needed)
# ===========================================

# Currency API (if using currency conversion features)
# CURRENCY_API_KEY=your-currency-api-key-here

# Email Configuration (if using email features)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# ===========================================
# DATABASE VARIABLES (Optional - SQLite Default)
# ===========================================

# PostgreSQL (if you want to upgrade from SQLite)
# DATABASE_URL=postgresql://username:password@host:port/database_name

# ===========================================
# FIREBASE VARIABLES (Already Configured)
# ===========================================

# Firebase configuration is already hardcoded in settings.py
# No additional environment variables needed for Firebase
# Your Firebase project: sma-student
# Service account credentials are embedded in settings.py

# ===========================================
# RENDER-SPECIFIC VARIABLES (Auto-Set by Render)
# ===========================================

# These are automatically set by Render, don't override:
# RENDER=true
# RENDER_EXTERNAL_HOSTNAME=your-app.onrender.com
# RENDER_EXTERNAL_URL=https://your-app.onrender.com

# ===========================================
# COPY-PASTE READY FORMAT
# ===========================================

# Copy these exact lines to your Render Environment Variables:

DEBUG=False
SECRET_KEY=v+@5rt&lx)tw4#e&4-+!-0a_z905rjp998i9ovpp^kpyg*7rxk

# ===========================================
# NOTES
# ===========================================

# 1. DEBUG=False is required for production
# 2. SECRET_KEY is generated securely - keep it secret!
# 3. Firebase works without additional env vars
# 4. SQLite database works without configuration
# 5. All other settings are configured in settings.py
# 6. Static files are handled by WhiteNoise automatically
# 7. CORS is configured for your domains
# 8. Security headers are enabled in production mode
