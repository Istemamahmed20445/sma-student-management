from django.conf import settings
from .firebase_config import get_firestore_client, get_storage_client
from google.cloud.firestore import FieldFilter
import uuid
from datetime import datetime
import json

class FirebaseManager:
    """Firebase operations manager"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.storage = get_storage_client()
    
    # Firestore Operations
    def create_document(self, collection, data, doc_id=None):
        """Create a new document in Firestore"""
        if doc_id:
            doc_ref = self.db.collection(collection).document(doc_id)
        else:
            doc_ref = self.db.collection(collection).document()
        
        # Add timestamps
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        doc_ref.set(data)
        return doc_ref.id
    
    def get_document(self, collection, doc_id):
        """Get a document from Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_document(self, collection, doc_id, data):
        """Update a document in Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        data['updated_at'] = datetime.utcnow()
        doc_ref.update(data)
        return True
    
    def delete_document(self, collection, doc_id):
        """Delete a document from Firestore"""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.delete()
        return True
    
    def query_documents(self, collection, filters=None, order_by=None, limit=None):
        """Query documents from Firestore"""
        query = self.db.collection(collection)
        
        if filters:
            for field, operator, value in filters:
                query = query.where(filter=FieldFilter(field, operator, value))
        
        if order_by:
            query = query.order_by(order_by)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    # Storage Operations
    def upload_file(self, file, path, content_type=None):
        """Upload file to Firebase Storage"""
        blob = self.storage.blob(path)
        
        if content_type:
            blob.content_type = content_type
        
        blob.upload_from_file(file)
        blob.make_public()
        
        return blob.public_url
    
    def delete_file(self, path):
        """Delete file from Firebase Storage"""
        blob = self.storage.blob(path)
        blob.delete()
        return True
    
    def get_file_url(self, path):
        """Get public URL for a file"""
        blob = self.storage.blob(path)
        return blob.public_url

# Student-specific Firebase operations
class StudentFirebaseManager(FirebaseManager):
    """Student-specific Firebase operations"""
    
    def sync_student_to_firestore(self, student):
        """Sync Django student model to Firestore"""
        data = {
            'student_id': student.student_id,
            'user_id': str(student.user.id),
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'email': student.user.email,
            'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
            'gender': student.gender,
            'nationality': student.nationality,
            'phone': student.phone,
            'address': student.address,
            'city': student.city,
            'state': student.state,
            'postal_code': student.postal_code,
            'country': student.country,
            'department_id': None,  # Department field removed
            'department_name': None,  # Department field removed
            'batch_id': str(student.batch.id) if student.batch else None,
            'batch_name': student.batch.name if student.batch else None,
            'enrollment_date': student.enrollment_date.isoformat(),
            'status': student.status,
            'emergency_contact_name': student.emergency_contact_name,
            'emergency_contact_phone': student.emergency_contact_phone,
            'emergency_contact_relationship': student.emergency_contact_relationship,
            'is_active': student.is_active,
        }
        
        return self.create_document('students', data, student.student_id)
    
    def sync_payment_transaction_to_firestore(self, transaction):
        """Sync Django PaymentTransaction model to Firestore"""
        data = {
            'transaction_id': str(transaction.id),
            'payment_id': str(transaction.payment.id),
            'student_id': transaction.payment.student.student_id,
            'batch_id': str(transaction.payment.batch.id),
            'amount': float(transaction.amount),
            'payment_method': transaction.payment_method,
            'payment_date': transaction.payment_date.isoformat(),
            'receipt_number': transaction.receipt_number,
            'processed_by': str(transaction.processed_by.id) if transaction.processed_by else None,
            'notes': transaction.notes,
            'is_active': transaction.is_active,
        }
        
        return self.create_document('payment_transactions', data, transaction.receipt_number)
    
    def sync_payment_to_firestore(self, payment):
        """Sync Django StudentPayment model to Firestore"""
        data = {
            'payment_id': str(payment.id),
            'student_id': payment.student.student_id,
            'batch_id': str(payment.batch.id),
            'total_amount': float(payment.total_amount),
            'currency_code': payment.currency.code,
            'currency_name': payment.currency.name,
            'payment_method': payment.payment_method,
            'status': payment.status,
            'notes': payment.notes,
            'created_by': str(payment.created_by.id) if payment.created_by else None,
            'is_active': payment.is_active,
        }
        
        return self.create_document('payments', data, str(payment.id))
    
    def sync_installment_to_firestore(self, installment):
        """Sync Django installment model to Firestore"""
        data = {
            'installment_id': str(installment.id),
            'student_id': installment.student.student_id,
            'batch_id': str(installment.batch.id),
            'fee_structure_id': str(installment.fee_structure.id),
            'installment_number': installment.installment_number,
            'due_date': installment.due_date.isoformat(),
            'amount': float(installment.amount),
            'currency_code': installment.currency.code,
            'status': installment.status,
            'paid_amount': float(installment.paid_amount),
            'paid_date': installment.paid_date.isoformat() if installment.paid_date else None,
            'late_fee': float(installment.late_fee),
            'notes': installment.notes,
            'is_active': installment.is_active,
        }
        
        return self.create_document('installments', data, str(installment.id))

# Initialize Firebase manager
firebase_manager = FirebaseManager()
student_firebase_manager = StudentFirebaseManager()
