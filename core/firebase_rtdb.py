"""
Firebase Firestore utilities for Student Management System
"""
from django.conf import settings
from .firebase_config import get_firestore_client
from datetime import datetime
import uuid

class FirebaseRTDBManager:
    """Firebase Firestore operations manager (using Firestore instead of RTDB)"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    def _add_timestamps(self, data):
        """Add timestamps to data"""
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()
        return data
    
    def create_student(self, student_data):
        """Create a new student in Firebase Firestore"""
        student_id = student_data.get('student_id', str(uuid.uuid4()))
        
        # Add timestamps
        student_data = self._add_timestamps(student_data)
        
        try:
            doc_ref = self.db.collection('students').document(student_id)
            doc_ref.set(student_data)
            return student_id
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_student(self, student_id):
        """Get a student from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('students').document(student_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def update_student(self, student_id, student_data):
        """Update a student in Firebase Firestore"""
        try:
            doc_ref = self.db.collection('students').document(student_id)
            student_data['updated_at'] = datetime.utcnow().isoformat()
            doc_ref.update(student_data)
            return True
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return False
    
    def delete_student(self, student_id):
        """Delete a student from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('students').document(student_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return False
    
    def get_all_students(self):
        """Get all students from Firebase Firestore"""
        try:
            docs = self.db.collection('students').stream()
            students = {}
            for doc in docs:
                students[doc.id] = doc.to_dict()
            return students
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return {}
    
    def create_payment(self, payment_data):
        """Create a new payment in Firebase Firestore"""
        payment_id = payment_data.get('payment_id', str(uuid.uuid4()))
        
        # Add timestamps
        payment_data = self._add_timestamps(payment_data)
        
        try:
            doc_ref = self.db.collection('payments').document(payment_id)
            doc_ref.set(payment_data)
            return payment_id
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_payment(self, payment_id):
        """Get a payment from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('payments').document(payment_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_student_payments(self, student_id):
        """Get all payments for a specific student"""
        try:
            docs = self.db.collection('payments').where('student_id', '==', student_id).stream()
            payments = {}
            for doc in docs:
                payments[doc.id] = doc.to_dict()
            return payments
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return {}
    
    def create_batch(self, batch_data):
        """Create a new batch in Firebase Firestore"""
        batch_id = batch_data.get('batch_id', str(uuid.uuid4()))
        
        # Add timestamps
        batch_data = self._add_timestamps(batch_data)
        
        try:
            doc_ref = self.db.collection('batches').document(batch_id)
            doc_ref.set(batch_data)
            return batch_id
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_batch(self, batch_id):
        """Get a batch from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('batches').document(batch_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_all_batches(self):
        """Get all batches from Firebase Firestore"""
        try:
            docs = self.db.collection('batches').stream()
            batches = {}
            for doc in docs:
                batches[doc.id] = doc.to_dict()
            return batches
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return {}
    
    def create_user(self, user_data):
        """Create a new user in Firebase Firestore"""
        user_id = user_data.get('user_id', str(uuid.uuid4()))
        
        # Add timestamps
        user_data = self._add_timestamps(user_data)
        
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(user_data)
            return user_id
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_user(self, user_id):
        """Get a user from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_all_users(self):
        """Get all users from Firebase Firestore"""
        try:
            docs = self.db.collection('users').stream()
            users = {}
            for doc in docs:
                users[doc.id] = doc.to_dict()
            return users
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return {}
    
    def create_contact(self, contact_data):
        """Create a new contact in Firebase Firestore"""
        contact_id = contact_data.get('contact_id', str(uuid.uuid4()))
        
        # Add timestamps
        contact_data = self._add_timestamps(contact_data)
        
        try:
            doc_ref = self.db.collection('contacts').document(contact_id)
            doc_ref.set(contact_data)
            return contact_id
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_contact(self, contact_id):
        """Get a contact from Firebase Firestore"""
        try:
            doc_ref = self.db.collection('contacts').document(contact_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return None
    
    def get_all_contacts(self):
        """Get all contacts from Firebase Firestore"""
        try:
            docs = self.db.collection('contacts').stream()
            contacts = {}
            for doc in docs:
                contacts[doc.id] = doc.to_dict()
            return contacts
        except Exception as e:
            print(f"Firebase Firestore Error: {e}")
            return {}

# Initialize Firebase Firestore manager
firebase_rtdb_manager = FirebaseRTDBManager()