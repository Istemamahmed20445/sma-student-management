#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_admin():
    """Create admin user if it doesn't exist"""
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@sma.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create user profile
        print("Creating user profile...")
        UserProfile.objects.create(
            user=admin_user,
            role='admin',
            phone='',
            address='',
            is_verified=True
        )
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists")
    
    # Test database connection
    user_count = User.objects.count()
    print(f"Total users in database: {user_count}")

if __name__ == '__main__':
    create_admin()
