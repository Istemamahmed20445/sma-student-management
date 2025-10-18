# Student Management System

A comprehensive Student Management System built with Django, Python, Tailwind CSS, and Firebase integration. This system supports multi-currency payments, installment-based fees, and batch management.

## Features

### 🎓 Core Features
- **Student Management**: Complete student profiles, academic records, and document management
- **Batch System**: Organize students into batches (Batch 57, Batch 59, etc.)
- **Multi-Currency Support**: BDT, USD, AUD, INR, PKR with real-time conversion
- **Installment Payments**: Flexible 2 or 3 installment payment plans
- **Academic Tracking**: Grades, attendance, and performance analytics
- **Role-Based Access**: Admin, Teacher, Student, and Parent portals

### 💰 Financial Management
- **Multi-Currency Fee Collection**: Support for 5 major currencies
- **Installment Tracking**: Automated payment reminders and late fee calculations
- **Payment Processing**: Multiple payment methods and gateway integration
- **Fee Waivers**: Scholarship and financial aid management
- **Refund System**: Complete refund processing and tracking

### 📊 Academic Management
- **Grade Management**: Weighted grading system with letter grades
- **Attendance Tracking**: Daily attendance with multiple status options
- **Course Management**: Subject catalog with prerequisites
- **Batch Scheduling**: Class schedules and room assignments
- **Academic Calendar**: Semester and academic year management

### 🔐 User Management
- **Authentication**: Secure login system with role-based access
- **User Profiles**: Extended profiles for different user types
- **Activity Tracking**: User activity and session management
- **Notifications**: System-wide and user-specific notifications

## Technology Stack

- **Backend**: Django 5.2.7, Django REST Framework
- **Frontend**: Tailwind CSS, Alpine.js, Font Awesome
- **Database**: SQLite (development), Firebase Firestore (production)
- **Storage**: Firebase Storage
- **Authentication**: Firebase Auth
- **Deployment**: Railway, Git

## Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Student Management System"
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env_example.txt .env
   ```
   Edit `.env` file with your Firebase credentials and settings.

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - Open http://127.0.0.1:8000 in your browser
   - Admin panel: http://127.0.0.1:8000/admin
   - Default admin credentials: admin/admin123

## Firebase Configuration

### Project Details
- **Project ID**: `sma-student`
- **Storage Bucket**: `sma-student.firebasestorage.app`
- **Auth Domain**: `sma-student.firebaseapp.com`

### Setup Steps
1. Firebase project is already configured: `sma-student`
2. Firestore Database and Storage are enabled
3. Service account key is configured in settings
4. Deploy Firebase rules: `./deploy_firebase.sh`
5. Initialize Firebase data: `python manage.py init_firebase`

### Firebase Services
- **Firestore**: Real-time database for student data, payments, grades
- **Storage**: File storage for documents, images, certificates
- **Authentication**: User authentication and role-based access
- **Security Rules**: Comprehensive security rules for data protection

## Project Structure

```
Student Management System/
├── core/                 # Core models and utilities
├── students/            # Student management
├── batches/             # Batch management
├── fees/                # Fee and payment management
├── accounts/            # User authentication and profiles
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploaded files
├── firebase_rules/      # Firebase security rules
├── requirements.txt     # Python dependencies
├── firebase.json        # Firebase configuration
├── deploy_firebase.sh   # Firebase deployment script
├── manage.py           # Django management script
├── README.md           # This file
└── FIREBASE_SETUP.md   # Firebase setup guide
```

## Usage

### For Administrators
- Manage students, batches, and courses
- Process applications and payments
- Generate reports and analytics
- Configure system settings

### For Teachers
- Manage assigned batches
- Enter grades and attendance
- View student progress
- Communicate with students

### For Students
- View academic progress
- Check fee status and installments
- Access course materials
- Update personal information

### For Parents
- Monitor child's academic progress
- View fee payments and due dates
- Communicate with teachers
- Access school announcements

## API Endpoints

- `/api/currency/convert/` - Currency conversion
- `/api/currency/rates/` - Exchange rates
- `/api/students/<id>/` - Student data
- `/api/batches/<id>/` - Batch information
- `/api/payments/` - Payment processing

## Deployment

### Railway Deployment
1. Connect your Git repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
# Firebase is already configured in settings.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

## Changelog

### Version 1.0.0
- Initial release
- Core student management features
- Multi-currency support
- Installment payment system
- Batch management
- Role-based access control
- Firebase integration (Firestore + Storage)
- Real-time data synchronization
- Comprehensive security rules
- File upload and management
