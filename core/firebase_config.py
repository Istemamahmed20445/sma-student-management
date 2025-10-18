import firebase_admin
from firebase_admin import credentials, firestore, storage
from django.conf import settings
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    if not firebase_admin._apps:
        # Create credentials from settings
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_CONFIG['project_id'],
            "private_key_id": settings.FIREBASE_CONFIG['private_key_id'],
            "private_key": settings.FIREBASE_CONFIG['private_key'],
            "client_email": settings.FIREBASE_CONFIG['client_email'],
            "client_id": settings.FIREBASE_CONFIG['client_id'],
            "auth_uri": settings.FIREBASE_CONFIG['auth_uri'],
            "token_uri": settings.FIREBASE_CONFIG['token_uri'],
            "auth_provider_x509_cert_url": settings.FIREBASE_CONFIG['auth_provider_x509_cert_url'],
            "client_x509_cert_url": settings.FIREBASE_CONFIG['client_x509_cert_url']
        })
        
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'sma-student.firebasestorage.app'
        })
    
    return firebase_admin.get_app()

# Get Firestore client
def get_firestore_client():
    """Get Firestore client instance"""
    initialize_firebase()
    return firestore.client()

# Get Storage client
def get_storage_client():
    """Get Firebase Storage client instance"""
    initialize_firebase()
    return storage.bucket()

# Currency conversion utilities
class CurrencyConverter:
    """Handle currency conversion and exchange rates"""
    
    SUPPORTED_CURRENCIES = {
        'BDT': 'Bangladeshi Taka',
        'USD': 'US Dollar',
        'AUD': 'Australian Dollar',
        'INR': 'Indian Rupee',
        'PKR': 'Pakistani Rupee'
    }
    
    @staticmethod
    def get_exchange_rates():
        """Get current exchange rates (mock implementation)"""
        # In production, integrate with a real currency API
        return {
            'USD': 1.0,
            'BDT': 110.0,  # 1 USD = 110 BDT
            'AUD': 1.5,    # 1 USD = 1.5 AUD
            'INR': 83.0,   # 1 USD = 83 INR
            'PKR': 280.0   # 1 USD = 280 PKR
        }
    
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        rates = CurrencyConverter.get_exchange_rates()
        
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        usd_amount = amount / rates.get(from_currency, 1)
        converted_amount = usd_amount * rates.get(to_currency, 1)
        
        return round(converted_amount, 2)
    
    @staticmethod
    def format_currency(amount, currency):
        """Format amount with currency symbol"""
        currency_symbols = {
            'USD': '$',
            'BDT': '৳',
            'AUD': 'A$',
            'INR': '₹',
            'PKR': '₨'
        }
        
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"
