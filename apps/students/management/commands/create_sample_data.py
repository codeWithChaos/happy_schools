from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import School, AcademicYear, Class, Section, Subject
from apps.students.models import Student, Guardian
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create School
        school, created = School.objects.get_or_create(
            name='Demo High School',
            defaults={
                'subdomain': 'demo',
                'email': 'admin@demo.school.com',
                'phone': '+1234567890',
                'address_line1': '123 Education Street',
                'city': 'Demo City',
                'state': 'Demo State',
                'postal_code': '12345',
                'country': 'United States',
                'subscription_status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created school: {school.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'School already exists: {school.name}'))

        # Create Academic Year
        academic_year, created = AcademicYear.objects.get_or_create(
            school=school,
            year='2024-2025',
            defaults={
                'start_date': date(2024, 9, 1),
                'end_date': date(2025, 6, 30),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created academic year: {academic_year.year}'))

        # Create Classes
        classes_data = [
            {'name': 'Grade 9', 'description': 'Ninth Grade'},
            {'name': 'Grade 10', 'description': 'Tenth Grade'},
            {'name': 'Grade 11', 'description': 'Eleventh Grade'},
            {'name': 'Grade 12', 'description': 'Twelfth Grade'},
        ]
        classes = []
        for class_data in classes_data:
            cls, created = Class.objects.get_or_create(
                school=school,
                name=class_data['name'],
                defaults={
                    'description': class_data['description'],
                    'academic_year': academic_year
                }
            )
            classes.append(cls)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created class: {cls.name}'))

        # Create Sections
        sections_data = [
            {'name': 'Section A', 'capacity': 40},
            {'name': 'Section B', 'capacity': 40},
            {'name': 'Section C', 'capacity': 40},
        ]
        sections = {}
        for cls in classes:
            sections[cls.id] = []
            for section_data in sections_data:
                section, created = Section.objects.get_or_create(
                    class_obj=cls,
                    name=section_data['name'],
                    defaults={'capacity': section_data['capacity']}
                )
                sections[cls.id].append(section)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created section: {cls.name} - {section.name}'))

        # Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@demo.school.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'school': school,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))

        # Create Teacher User
        teacher_user, created = User.objects.get_or_create(
            username='teacher',
            defaults={
                'email': 'teacher@demo.school.com',
                'first_name': 'John',
                'last_name': 'Teacher',
                'role': 'teacher',
                'school': school
            }
        )
        if created:
            teacher_user.set_password('teacher123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created teacher user: {teacher_user.username}'))

        # Create Sample Students with Guardians
        students_data = [
            {
                'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'M',
                'admission_number': 'STU2024001', 'date_of_birth': date(2009, 3, 15),
                'blood_group': 'A+', 'email': 'alice.j@student.demo.com',
                'class': classes[0], 'section': sections[classes[0].id][0],
                'roll_number': '1'
            },
            {
                'first_name': 'Bob', 'last_name': 'Smith', 'gender': 'M',
                'admission_number': 'STU2024002', 'date_of_birth': date(2009, 7, 22),
                'blood_group': 'B+', 'email': 'bob.s@student.demo.com',
                'class': classes[0], 'section': sections[classes[0].id][0],
                'roll_number': '2'
            },
            {
                'first_name': 'Carol', 'last_name': 'Williams', 'gender': 'F',
                'admission_number': 'STU2024003', 'date_of_birth': date(2009, 11, 8),
                'blood_group': 'O+', 'email': 'carol.w@student.demo.com',
                'class': classes[0], 'section': sections[classes[0].id][1],
                'roll_number': '3'
            },
            {
                'first_name': 'David', 'last_name': 'Brown', 'gender': 'M',
                'admission_number': 'STU2024004', 'date_of_birth': date(2008, 5, 19),
                'blood_group': 'AB+', 'email': 'david.b@student.demo.com',
                'class': classes[1], 'section': sections[classes[1].id][0],
                'roll_number': '1'
            },
            {
                'first_name': 'Emma', 'last_name': 'Davis', 'gender': 'F',
                'admission_number': 'STU2024005', 'date_of_birth': date(2008, 9, 30),
                'blood_group': 'A-', 'email': 'emma.d@student.demo.com',
                'class': classes[1], 'section': sections[classes[1].id][0],
                'roll_number': '2'
            },
            {
                'first_name': 'Frank', 'last_name': 'Miller', 'gender': 'M',
                'admission_number': 'STU2024006', 'date_of_birth': date(2008, 12, 5),
                'blood_group': 'B-', 'email': 'frank.m@student.demo.com',
                'class': classes[1], 'section': sections[classes[1].id][1],
                'roll_number': '3'
            },
            {
                'first_name': 'Grace', 'last_name': 'Wilson', 'gender': 'F',
                'admission_number': 'STU2024007', 'date_of_birth': date(2007, 2, 14),
                'blood_group': 'O-', 'email': 'grace.w@student.demo.com',
                'class': classes[2], 'section': sections[classes[2].id][0],
                'roll_number': '1'
            },
            {
                'first_name': 'Henry', 'last_name': 'Moore', 'gender': 'M',
                'admission_number': 'STU2024008', 'date_of_birth': date(2007, 6, 28),
                'blood_group': 'AB-', 'email': 'henry.m@student.demo.com',
                'class': classes[2], 'section': sections[classes[2].id][1],
                'roll_number': '2'
            },
            {
                'first_name': 'Ivy', 'last_name': 'Taylor', 'gender': 'F',
                'admission_number': 'STU2023001', 'date_of_birth': date(2006, 10, 10),
                'blood_group': 'A+', 'email': 'ivy.t@student.demo.com',
                'class': classes[3], 'section': sections[classes[3].id][0],
                'roll_number': '1'
            },
            {
                'first_name': 'Jack', 'last_name': 'Anderson', 'gender': 'M',
                'admission_number': 'STU2024009', 'date_of_birth': date(2006, 4, 17),
                'blood_group': 'B+', 'email': 'jack.a@student.demo.com',
                'class': classes[3], 'section': sections[classes[3].id][0],
                'roll_number': '2'
            },
        ]

        for student_data in students_data:
            # Create student user
            username = f"{student_data['first_name'].lower()}.{student_data['last_name'].lower()}"
            student_user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'role': 'student',
                    'school': school,
                    'date_of_birth': student_data['date_of_birth']
                }
            )
            if user_created:
                student_user.set_password('student123')
                student_user.save()

            # Create student
            student, created = Student.objects.get_or_create(
                school=school,
                user=student_user,
                defaults={
                    'admission_number': student_data['admission_number'],
                    'gender': student_data['gender'],
                    'blood_group': student_data['blood_group'],
                    'class_assigned': student_data['class'],
                    'section': student_data['section'],
                    'roll_number': student_data['roll_number'],
                    'date_of_admission': timezone.now().date() - timedelta(days=365)
                }
            )

            if created:
                # Create guardian for each student
                guardian_username = f"guardian.{student_data['last_name'].lower()}"
                guardian_user, guardian_user_created = User.objects.get_or_create(
                    username=guardian_username,
                    defaults={
                        'email': f"guardian.{student_data['last_name'].lower()}@demo.com",
                        'first_name': f"Mr./Mrs.",
                        'last_name': student_data['last_name'],
                        'role': 'parent',
                        'school': school,
                        'phone': f"+123456789{student_data['roll_number']}"
                    }
                )
                if guardian_user_created:
                    guardian_user.set_password('guardian123')
                    guardian_user.save()

                guardian, guardian_created = Guardian.objects.get_or_create(
                    user=guardian_user,
                    defaults={
                        'school': school,
                        'relation': 'father',
                        'occupation': 'Professional'
                    }
                )

                # Link guardian to student
                student.guardians.add(guardian)

                self.stdout.write(self.style.SUCCESS(
                    f'Created student: {student.user.get_full_name()} ({student.admission_number})'
                ))

        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Creation Complete! ==='))
        self.stdout.write(self.style.SUCCESS('\nCredentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: username=admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('Teacher: username=teacher, password=teacher123'))
        self.stdout.write(self.style.SUCCESS('Students: username=firstname.lastname, password=student123'))
        self.stdout.write(self.style.SUCCESS('\nAccess the application at: http://127.0.0.1:8000/'))
