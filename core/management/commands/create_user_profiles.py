from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for users who don\'t have one'

    def handle(self, *args, **options):
        self.stdout.write('Creating UserProfiles for users without profiles...')
        
        try:
            users_without_profiles = User.objects.filter(profile__isnull=True)
            created_count = 0
            
            for user in users_without_profiles:
                try:
                    UserProfile.objects.create(
                        user=user,
                        role='student',  # Default role
                        phone='',
                        address='',
                        bio='',
                        language='en',
                        timezone='UTC',
                        theme='light',
                        is_verified=False
                    )
                    created_count += 1
                    self.stdout.write(f'Created profile for user: {user.username}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating profile for {user.username}: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} UserProfiles!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating UserProfiles: {str(e)}')
            )
