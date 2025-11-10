"""
Management command to test authentication
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from apps.accounts.models import School, User


class Command(BaseCommand):
    help = 'Test authentication with different formats'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test')
        parser.add_argument('password', type=str, help='Password to test')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        self.stdout.write(f'\nTesting authentication for: {username}')
        self.stdout.write('=' * 60)
        
        user = authenticate(username=username, password=password)
        
        if user:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Authentication SUCCESSFUL!'))
            self.stdout.write(f'  User: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Role: {user.role}')
            self.stdout.write(f'  School: {user.school.name if user.school else "No school"}')
            self.stdout.write(f'  Active: {user.is_active}')
        else:
            self.stdout.write(self.style.ERROR(f'\n✗ Authentication FAILED!'))
            self.stdout.write(self.style.WARNING('\nChecking what went wrong...'))
            
            # Try to identify the issue
            if '/' in username:
                school_name, user_identifier = username.split('/', 1)
                school_name = school_name.strip()
                user_identifier = user_identifier.strip()
                
                # Check if school exists
                from django.db.models import Q
                schools = School.objects.filter(
                    Q(name__iexact=school_name) | Q(subdomain__iexact=school_name)
                )
                
                if not schools.exists():
                    self.stdout.write(self.style.ERROR(f'  ✗ School not found: "{school_name}"'))
                    self.stdout.write('\n  Available schools:')
                    for s in School.objects.all():
                        self.stdout.write(f'    - {s.name} (subdomain: {s.subdomain})')
                else:
                    school = schools.first()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ School found: {school.name}'))
                    
                    # Check if user exists in that school
                    users = User.objects.filter(
                        Q(email__iexact=user_identifier) | Q(username__iexact=user_identifier),
                        school=school
                    )
                    
                    if not users.exists():
                        self.stdout.write(self.style.ERROR(f'  ✗ User not found: "{user_identifier}" in school "{school.name}"'))
                        self.stdout.write(f'\n  Users in {school.name}:')
                        for u in User.objects.filter(school=school):
                            self.stdout.write(f'    - {u.username} ({u.email})')
                    else:
                        user_obj = users.first()
                        self.stdout.write(self.style.SUCCESS(f'  ✓ User found: {user_obj.username}'))
                        self.stdout.write(self.style.ERROR('  ✗ Password incorrect or user inactive'))
                        self.stdout.write(f'    User active: {user_obj.is_active}')
            else:
                # No school specified
                self.stdout.write(self.style.WARNING('  No school specified (no "/" in username)'))
                self.stdout.write('  Try format: SchoolName/email or SchoolName/username')
