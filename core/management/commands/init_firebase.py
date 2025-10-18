from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Currency, AcademicYear, Semester
from core.firebase_utils import firebase_manager
from accounts.models import UserProfile
import json

class Command(BaseCommand):
    help = 'Initialize Firebase with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Firebase...')
        
        try:
            # Initialize currencies
            self.init_currencies()
            
            # Departments removed
            
            # Initialize academic years
            self.init_academic_years()
            
            # Initialize system settings
            self.init_system_settings()
            
            self.stdout.write(
                self.style.SUCCESS('Firebase initialization completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing Firebase: {str(e)}')
            )

    def init_currencies(self):
        """Initialize currency data in Firebase"""
        self.stdout.write('Initializing currencies...')
        
        currencies = [
            {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': '$',
                'exchange_rate': 1.0,
                'is_default': True,
                'is_active': True
            },
            {
                'code': 'BDT',
                'name': 'Bangladeshi Taka',
                'symbol': '৳',
                'exchange_rate': 110.0,
                'is_default': False,
                'is_active': True
            },
            {
                'code': 'AUD',
                'name': 'Australian Dollar',
                'symbol': 'A$',
                'exchange_rate': 1.5,
                'is_default': False,
                'is_active': True
            },
            {
                'code': 'INR',
                'name': 'Indian Rupee',
                'symbol': '₹',
                'exchange_rate': 83.0,
                'is_default': False,
                'is_active': True
            },
            {
                'code': 'PKR',
                'name': 'Pakistani Rupee',
                'symbol': '₨',
                'exchange_rate': 280.0,
                'is_default': False,
                'is_active': True
            }
        ]
        
        for currency in currencies:
            firebase_manager.create_document('currencies', currency, currency['code'])
        
        self.stdout.write('Currencies initialized successfully!')

    # Department initialization removed

    def init_academic_years(self):
        """Initialize academic year data in Firebase"""
        self.stdout.write('Initializing academic years...')
        
        academic_years = [
            {
                'name': '2024-2025',
                'start_date': '2024-09-01',
                'end_date': '2025-08-31',
                'is_current': True,
                'is_active': True
            },
            {
                'name': '2023-2024',
                'start_date': '2023-09-01',
                'end_date': '2024-08-31',
                'is_current': False,
                'is_active': True
            }
        ]
        
        for year in academic_years:
            firebase_manager.create_document('academic_years', year, year['name'])
        
        self.stdout.write('Academic years initialized successfully!')

    def init_system_settings(self):
        """Initialize system settings in Firebase"""
        self.stdout.write('Initializing system settings...')
        
        settings = [
            {
                'key': 'max_file_size',
                'value': '10MB',
                'description': 'Maximum file upload size',
                'category': 'upload'
            },
            {
                'key': 'allowed_file_types',
                'value': 'pdf,doc,docx,jpg,jpeg,png',
                'description': 'Allowed file types for upload',
                'category': 'upload'
            },
            {
                'key': 'late_fee_rate',
                'value': '0.05',
                'description': 'Late fee rate (5% per month)',
                'category': 'fees'
            },
            {
                'key': 'default_installments',
                'value': '2',
                'description': 'Default number of installments',
                'category': 'fees'
            },
            {
                'key': 'system_name',
                'value': 'Student Management System',
                'description': 'System name',
                'category': 'general'
            },
            {
                'key': 'system_version',
                'value': '1.0.0',
                'description': 'System version',
                'category': 'general'
            }
        ]
        
        for setting in settings:
            firebase_manager.create_document('settings', setting, setting['key'])
        
        self.stdout.write('System settings initialized successfully!')
