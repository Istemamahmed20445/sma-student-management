#!/usr/bin/env python3
"""
Simple script to create admin user for local development
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_admin():
    try:
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            print('👤 Creating admin user...')
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@sma.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=admin_user,
                role='admin',
                phone='',
                address='',
                is_verified=True
            )
            
            print('✅ Admin user created successfully!')
            print('📝 Login credentials:')
            print('   Username: admin')
            print('   Password: admin123')
        else:
            print('ℹ️  Admin user already exists')
        
        # Show user count
        user_count = User.objects.count()
        print(f'📊 Total users in database: {user_count}')
        
    except Exception as e:
        print(f'❌ Error creating admin user: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    create_admin()
