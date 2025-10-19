from django.core.management.base import BaseCommand
from core.models import Currency

class Command(BaseCommand):
    help = 'Initialize currencies in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing currencies...')
        
        try:
            # Define currencies to create
            currencies_data = [
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
            
            created_count = 0
            updated_count = 0
            
            for currency_data in currencies_data:
                currency, created = Currency.objects.get_or_create(
                    code=currency_data['code'],
                    defaults=currency_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created currency: {currency.code} - {currency.name}')
                else:
                    # Update existing currency if needed
                    updated = False
                    for key, value in currency_data.items():
                        if key != 'code' and getattr(currency, key) != value:
                            setattr(currency, key, value)
                            updated = True
                    
                    if updated:
                        currency.save()
                        updated_count += 1
                        self.stdout.write(f'Updated currency: {currency.code} - {currency.name}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Currency initialization completed! Created: {created_count}, Updated: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing currencies: {str(e)}')
            )
