# Firebase Setup Guide

This guide will help you set up Firebase for your Student Management System.

## Prerequisites

1. Firebase project created: `sma-student`
2. Firebase CLI installed: `npm install -g firebase-tools`
3. Service account key downloaded

## Firebase Configuration

### Project Details
- **Project ID**: `sma-student`
- **Storage Bucket**: `sma-student.firebasestorage.app`
- **Auth Domain**: `sma-student.firebaseapp.com`

### Web Config
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyAC6jhWOKd06VhjV7RTyntVZwkDPGDcf-4",
  authDomain: "sma-student.firebaseapp.com",
  projectId: "sma-student",
  storageBucket: "sma-student.firebasestorage.app",
  messagingSenderId: "621019846757",
  appId: "1:621019846757:web:02faa1536bbb73969e0e8c"
};
```

## Setup Steps

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
```

### 2. Login to Firebase
```bash
firebase login
```

### 3. Initialize Firebase in your project
```bash
cd "Student Management System"
firebase init
```

Select the following options:
- **Firestore**: Configure security rules and indexes
- **Storage**: Configure security rules
- **Hosting**: Configure files for Firebase Hosting (optional)

### 4. Deploy Firestore Rules
```bash
firebase deploy --only firestore:rules
```

### 5. Deploy Storage Rules
```bash
firebase deploy --only storage
```

### 6. Initialize Firebase Data
```bash
python manage.py init_firebase
```

## Firebase Services Used

### 1. Firestore Database
- **Collections**:
  - `students` - Student profiles and information
  - `payments` - Payment records
  - `installments` - Fee installment tracking
  - `batches` - Batch information
  - `grades` - Student grades
  - `attendance` - Attendance records
  - `user_profiles` - User profile data
  - `currencies` - Currency exchange rates
  - `settings` - System settings

### 2. Firebase Storage
- **Folders**:
  - `student_profiles/` - Student profile images
  - `student_documents/` - Student documents
  - `user_profiles/` - User profile images
  - `course_materials/` - Course materials
  - `assignments/` - Assignment submissions
  - `certificates/` - Certificates and transcripts
  - `receipts/` - Payment receipts

### 3. Firebase Authentication
- User authentication and authorization
- Role-based access control
- Custom claims for user roles

## Security Rules

### Firestore Rules
The Firestore rules are configured in `firebase_rules/firestore.rules` and provide:
- Role-based access control
- User-specific data access
- Admin-only operations
- Secure data isolation

### Storage Rules
The Storage rules are configured in `firebase_rules/storage.rules` and provide:
- File upload restrictions
- User-specific file access
- Size and type limitations
- Secure file organization

## Data Synchronization

The system automatically synchronizes data between Django and Firebase using Django signals:

- **Student data** syncs when students are created/updated
- **Payment data** syncs when payments are processed
- **Grade data** syncs when grades are entered
- **Attendance data** syncs when attendance is marked
- **User profiles** sync when user data changes

## Firebase Functions (Optional)

You can create Firebase Cloud Functions for:
- Automatic file cleanup
- Email notifications
- Payment processing webhooks
- Data backup and archiving

## Monitoring and Analytics

Enable Firebase Analytics to track:
- User engagement
- Feature usage
- Performance metrics
- Error tracking

## Backup and Recovery

### Firestore Backup
```bash
# Export Firestore data
gcloud firestore export gs://your-backup-bucket/firestore-backup

# Import Firestore data
gcloud firestore import gs://your-backup-bucket/firestore-backup
```

### Storage Backup
```bash
# Backup storage bucket
gsutil -m cp -r gs://sma-student.firebasestorage.app gs://your-backup-bucket/storage-backup
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check service account key
   - Verify project ID
   - Ensure proper permissions

2. **Storage Upload Failures**
   - Check storage rules
   - Verify file size limits
   - Check file type restrictions

3. **Firestore Connection Issues**
   - Verify network connectivity
   - Check Firestore rules
   - Ensure proper indexing

### Debug Mode
Enable debug logging in Django settings:
```python
import logging
logging.getLogger('firebase_admin').setLevel(logging.DEBUG)
```

## Production Considerations

1. **Security**
   - Use environment variables for sensitive data
   - Implement proper authentication
   - Regular security audits

2. **Performance**
   - Optimize Firestore queries
   - Use proper indexing
   - Implement caching strategies

3. **Scalability**
   - Monitor usage limits
   - Implement pagination
   - Use batch operations

4. **Cost Optimization**
   - Monitor Firebase usage
   - Optimize storage usage
   - Implement data archiving

## Support

For Firebase-related issues:
1. Check Firebase Console
2. Review Firebase Documentation
3. Contact Firebase Support
4. Check system logs for errors
