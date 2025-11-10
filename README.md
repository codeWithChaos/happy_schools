# School Management System

A comprehensive multi-tenant Django-based school management system that enables multiple schools to manage their operations independently within a single application instance.

## 🎯 Overview

This system provides a complete solution for educational institutions to manage students, teachers, parents, attendance, fees, examinations, timetables, and internal communications. Built with Django 5.2.8 and featuring role-based dashboards with real-time statistics and visualizations.

## ✨ Key Features

### Multi-Tenancy
- Complete data isolation between schools
- Single codebase serving multiple institutions
- School-specific branding and configuration

### User Management
- Four user roles: Admin, Teacher, Student, Parent
- Role-based access control and permissions
- Secure authentication and authorization

### Academic Structure
- Class and section management
- Subject assignment and tracking
- Academic year configuration
- Student enrollment and class assignments

### Attendance System
- Daily attendance marking with bulk operations
- Real-time attendance statistics and reports
- Multiple status options: Present, Absent, Late, Excused
- Teacher-based attendance tracking
- Date-wise and class-wise filtering

### Fee Management
- Flexible fee structure configuration
- Multiple payment methods (Cash, Card, Online, Check)
- Payment tracking with receipt generation
- Partial payment support
- Late fee and discount management
- Payment status tracking: Pending, Completed, Failed, Refunded, Cancelled
- Comprehensive fee collection reports

### Timetable Management
- Period-wise class scheduling
- Teacher assignment to periods
- Day-wise timetable view (Monday-Saturday)
- Room allocation
- Break and lab session marking
- Conflict detection and validation

### Examination System
- Multiple exam types: Unit Test, Mid-Term, Final, Quarterly, etc.
- Exam scheduling with date ranges
- Multi-class exam assignment
- Subject-wise marks entry
- Automatic grade calculation (A+, A, B+, B, C+, C, D, F)
- Theory and practical marks separation
- Student result management
- Pass/fail status tracking

### Communications
- System-wide announcements
- Internal messaging between users
- Priority-based notifications (Normal, High, Urgent)
- Target audience filtering (All, Students, Teachers, Parents)
- Inbox/Sent folders
- Message starring and deletion
- Unread message indicators

### Dashboard & Reports
- **Admin Dashboard:**
  - Student, teacher, and class statistics
  - Today's attendance overview
  - Fee collection metrics (collected vs pending)
  - Recent and upcoming exams
  - Attendance trend chart (7 days)
  - Fee collection trend chart (30 days)
  - Recent payments and announcements
  
- **Teacher Dashboard:**
  - Classes taught overview
  - Today's attendance for assigned classes
  - Quick actions: Mark attendance, Enter marks, View timetable
  - Upcoming exams for teaching classes
  - Assigned classes with student counts
  
- **Student Dashboard:**
  - Personal attendance statistics (30 days)
  - Fee payment status
  - Recent exam results with grades
  - Upcoming exams for enrolled class
  - Quick access to timetable and results
  
- **Parent Dashboard:**
  - Multi-child overview
  - Per-child attendance and fee status
  - Children's recent exam results
  - Direct access to announcements

### Search Functionality
- Global search across students, teachers, announcements, and exams
- Role-based result filtering
- Quick access to detailed views

## 🛠️ Technology Stack

- **Backend Framework:** Django 5.2.8
- **Python Version:** 3.13.3
- **Database:** SQLite (development) - PostgreSQL ready
- **Frontend:** Tailwind CSS 3.x
- **Charts:** Chart.js 4.4.0
- **Authentication:** Django built-in auth system
- **Forms:** Django ModelForms with custom templates

## 📋 Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git (for version control)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd schoolManagement
```

### 2. Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv schoolenv
.\schoolenv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv schoolenv
source schoolenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
schoolManagement/
├── apps/
│   ├── accounts/          # User, School, Class, Section, Subject models
│   ├── students/          # Student and Guardian management
│   ├── attendance/        # Attendance tracking system
│   ├── fees/              # Fee structure and payment management
│   ├── timetable/         # Class scheduling and timetable
│   ├── examinations/      # Exam and result management
│   ├── communications/    # Announcements, messages, notifications
│   └── dashboard/         # Dashboard views and statistics
├── templates/
│   ├── accounts/          # Authentication templates
│   ├── students/          # Student management templates
│   ├── attendance/        # Attendance templates
│   ├── fees/              # Fee management templates
│   ├── timetable/         # Timetable templates
│   ├── examinations/      # Examination templates
│   ├── communications/    # Communication templates
│   ├── dashboard/         # Dashboard templates
│   ├── components/        # Reusable components (sidebar, navbar)
│   └── base.html          # Base template
├── config/
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── middleware/
│   └── tenant.py          # Multi-tenancy middleware
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

## 🔐 User Roles & Permissions

### Admin
- Full system access
- Manage students, teachers, and guardians
- Configure fee structures
- Create and manage exams
- View all reports and statistics
- Manage school settings

### Teacher
- Mark attendance for assigned classes
- Enter exam marks
- View assigned class timetables
- Create announcements
- View student information
- Access teaching schedule

### Student
- View personal attendance records
- Check fee payment status
- View exam results and grades
- Access class timetable
- Read announcements
- View messages and notifications

### Parent
- View children's attendance
- Check fee status for all wards
- View children's exam results
- Access announcements
- Communicate with school staff

## 🔧 Configuration

### Multi-Tenancy Setup

The system uses middleware to identify the school based on the logged-in user:

```python
# middleware/tenant.py
class TenantMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            request.school = request.user.school
            request.academic_year = get_active_academic_year(request.user.school)
```

All queries automatically filter by school to ensure data isolation.

### Environment Variables (Production)

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📊 Database Models

### Core Models

- **School:** Multi-tenant school information
- **User:** Extended Django user with role field
- **AcademicYear:** Academic session management
- **Class:** Grade/class definition
- **Section:** Class sections (A, B, C, etc.)
- **Subject:** Subject management

### Student Models

- **Student:** Student profile and enrollment
- **Guardian:** Parent/guardian information

### Operational Models

- **Attendance:** Daily attendance records
- **FeeStructure:** Fee configuration
- **FeePayment:** Payment transactions
- **Timetable:** Period scheduling
- **Exam:** Examination configuration
- **ExamResult:** Student marks and grades
- **Announcement:** System announcements
- **Message:** Internal messaging
- **Notification:** System notifications

## 🎨 UI/UX Features

- Responsive design (mobile, tablet, desktop)
- Tailwind CSS utility-first styling
- Chart.js data visualizations
- Role-based navigation
- Breadcrumb navigation
- Real-time notifications
- Search functionality
- Filtering and sorting
- Pagination for large datasets

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.students

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Development Phases

- ✅ Phase 1: School & User Management
- ✅ Phase 2: Academic Structure
- ✅ Phase 3: Student Management
- ✅ Phase 4: Attendance System
- ✅ Phase 5: Fee Management
- ✅ Phase 6: Timetable Management
- ✅ Phase 7: Examination System
- ✅ Phase 8: Communications
- ✅ Phase 9: Dashboard & Reports
- ⏳ Phase 10: Testing & Documentation

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG = False` in settings
2. Configure production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend for notifications
5. Set secure `SECRET_KEY`
6. Enable HTTPS
7. Configure allowed hosts
8. Set up backup strategy
9. Configure logging
10. Run security checks: `python manage.py check --deploy`

### Deployment Options

- **Heroku:** Use `Procfile` and `runtime.txt`
- **AWS:** EC2 + RDS with Gunicorn and Nginx
- **DigitalOcean:** App Platform or Droplet
- **PythonAnywhere:** Beginner-friendly option

## 🔒 Security Features

- CSRF protection on all forms
- Role-based access control
- Data isolation per school
- SQL injection prevention (Django ORM)
- XSS protection
- Password hashing (PBKDF2)
- Session security
- Permission-based views

## 🐛 Known Issues & Limitations

- Currently uses SQLite (not recommended for production)
- Email functionality requires configuration
- No automated backup system
- Limited report export options (PDF, Excel to be added)
- No mobile app (web-based only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Initial Development - [Lawrence Dotse]

## 🙏 Acknowledgments

- Django framework and community
- Tailwind CSS team
- Chart.js developers
- All contributors

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: codewithchaos1809@gmail.com

## 🗺️ Roadmap

### Upcoming Features

- [ ] PDF report generation
- [ ] Excel export functionality
- [ ] Email notification system
- [ ] SMS integration
- [ ] Mobile responsive improvements
- [ ] Bulk data import (CSV)
- [ ] Advanced analytics dashboard
- [ ] Library management module
- [ ] Transport management
- [ ] Hostel management
- [ ] Staff payroll system
- [ ] Online exam module
- [ ] Parent mobile app
- [ ] API for third-party integrations

## 📸 Screenshots

### Admin Dashboard
![Admin Dashboard](screenshots/admin-dashboard.png)

### Student Management
![Student List](screenshots/student-list.png)

### Attendance Marking
![Attendance](screenshots/attendance.png)

### Fee Management
![Fee Management](screenshots/fees.png)

### Examination Results
![Results](screenshots/results.png)

---

**Built with ❤️ using Django**
