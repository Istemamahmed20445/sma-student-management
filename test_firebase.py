#!/usr/bin/env python
"""
Test Firebase Realtime Database connection
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')
django.setup()

from core.firebase_rtdb import firebase_rtdb_manager

def test_firebase_connection():
    """Test Firebase Firestore connection"""
    print("🔥 Testing Firebase Firestore Connection...")
    print("=" * 50)
    
    try:
        # Test basic connection by trying to read from the database
        print("📡 Testing connection...")
        result = firebase_rtdb_manager.get_all_students()
        
        if result is not None:
            print("✅ Firebase connection successful!")
            
            # Test creating a test student
            print("\n📝 Testing student creation...")
            test_student = {
                'student_id': 'TEST001',
                'first_name': 'Test',
                'last_name': 'Student',
                'email': 'test@example.com',
                'phone': '+1234567890',
                'status': 'active'
            }
            
            student_id = firebase_rtdb_manager.create_student(test_student)
            if student_id:
                print(f"✅ Test student created with ID: {student_id}")
                
                # Test reading the student
                print("\n📖 Testing student retrieval...")
                retrieved_student = firebase_rtdb_manager.get_student(student_id)
                if retrieved_student:
                    print("✅ Test student retrieved successfully!")
                    print(f"   Name: {retrieved_student.get('first_name')} {retrieved_student.get('last_name')}")
                    print(f"   Email: {retrieved_student.get('email')}")
                    
                    # Clean up test data
                    print("\n🧹 Cleaning up test data...")
                    firebase_rtdb_manager.delete_student(student_id)
                    print("✅ Test data cleaned up!")
                else:
                    print("❌ Failed to retrieve test student")
            else:
                print("❌ Failed to create test student")
        else:
            print("❌ Firebase connection failed!")
            
    except Exception as e:
        print(f"❌ Error testing Firebase connection: {str(e)}")
        return False
    
    print("\n🎉 Firebase Firestore test completed!")
    return True

if __name__ == '__main__':
    test_firebase_connection()
