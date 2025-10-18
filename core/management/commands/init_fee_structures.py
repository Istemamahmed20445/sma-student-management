from django.core.management.base import BaseCommand
from core.models import Currency, FeeStructure

class Command(BaseCommand):
    help = 'Initialize default fee structures for the medical academy'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing fee structures...')
        
        try:
            # Get or create currencies
            usd_currency, _ = Currency.objects.get_or_create(
                code='USD',
                defaults={
                    'name': 'United States Dollar',
                    'symbol': '$',
                    'exchange_rate': 1.0,
                    'is_default': True,
                    'is_active': True
                }
            )
            
            bdt_currency, _ = Currency.objects.get_or_create(
                code='BDT',
                defaults={
                    'name': 'Bangladeshi Taka',
                    'symbol': '৳',
                    'exchange_rate': 110.0,
                    'is_default': False,
                    'is_active': True
                }
            )
            
            # Create fee structures
            fee_structures = [
                {
                    'name': 'Medical Course - Full Program',
                    'description': 'Complete medical course program with all modules',
                    'total_amount': 50000.00,
                    'currency': usd_currency,
                    'installment_count': 3,
                    'is_active': True
                },
                {
                    'name': 'Medical Course - Full Program (BDT)',
                    'description': 'Complete medical course program in Bangladeshi Taka',
                    'total_amount': 5500000.00,
                    'currency': bdt_currency,
                    'installment_count': 3,
                    'is_active': True
                },
                {
                    'name': 'Basic Medical Training',
                    'description': 'Basic medical training program',
                    'total_amount': 25000.00,
                    'currency': usd_currency,
                    'installment_count': 2,
                    'is_active': True
                },
                {
                    'name': 'Advanced Medical Course',
                    'description': 'Advanced medical course with specialization',
                    'total_amount': 75000.00,
                    'currency': usd_currency,
                    'installment_count': 4,
                    'is_active': True
                },
                {
                    'name': 'Short Course - Medical Basics',
                    'description': 'Short course covering medical basics',
                    'total_amount': 10000.00,
                    'currency': usd_currency,
                    'installment_count': 2,
                    'is_active': True
                }
            ]
            
            for fee_data in fee_structures:
                fee_structure, created = FeeStructure.objects.get_or_create(
                    name=fee_data['name'],
                    defaults=fee_data
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created fee structure: {fee_structure.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Fee structure already exists: {fee_structure.name}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS('Fee structures initialization completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Fee structures initialization failed: {e}')
            )
