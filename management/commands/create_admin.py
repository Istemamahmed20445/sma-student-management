from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create admin user for production deployment'

    def handle(self, *args, **options):
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
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
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created admin user')
            )
            self.stdout.write('Username: admin')
            self.stdout.write('Password: admin123')
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
