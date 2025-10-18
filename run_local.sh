#!/bin/bash
set -e  # Exit on any error

echo "🚀 Starting Student Management System on Local Network..."
echo "=================================================="

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

echo "📱 Local IP Address: $LOCAL_IP"
echo "🌐 Access URLs:"
echo "   - Local: http://localhost:8000"
echo "   - Network: http://$LOCAL_IP:8000"
echo "=================================================="

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Run migrations (for Django's internal tables)
echo "📊 Running database migrations..."
python manage.py migrate

# Test Firebase connection
echo "🔥 Testing Firebase connection..."
python test_firebase.py

# Create admin user if it doesn't exist
echo "👤 Creating admin user..."
python create_local_admin.py

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "🚀 Starting Django development server..."
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start Django server on all interfaces
python manage.py runserver 0.0.0.0:8000
