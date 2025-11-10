"""
Management command to check authentication setup
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import School, User


class Command(BaseCommand):
    help = 'Check authentication setup - list schools and users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== SCHOOLS ==='))
        schools = School.objects.all()
        
        if not schools:
            self.stdout.write(self.style.WARNING('No schools found!'))
        else:
            for school in schools:
                self.stdout.write(f'\nSchool: {school.name}')
                self.stdout.write(f'  Subdomain: {school.subdomain}')
                self.stdout.write(f'  Email: {school.email}')
                self.stdout.write(f'  Active: {school.is_active}')
                
                # List users in this school
                users = User.objects.filter(school=school)
                self.stdout.write(f'  Users ({users.count()}):')
                for user in users:
                    self.stdout.write(f'    - {user.username} ({user.email}) - Role: {user.role} - Active: {user.is_active}')
        
        self.stdout.write(self.style.SUCCESS('\n=== USERS WITHOUT SCHOOL ==='))
        orphan_users = User.objects.filter(school__isnull=True)
        if not orphan_users:
            self.stdout.write(self.style.SUCCESS('All users have schools assigned!'))
        else:
            self.stdout.write(self.style.WARNING(f'Found {orphan_users.count()} users without schools:'))
            for user in orphan_users:
                self.stdout.write(f'  - {user.username} ({user.email}) - Role: {user.role}')
        
        self.stdout.write(self.style.SUCCESS('\n=== AUTHENTICATION TEST EXAMPLES ==='))
        if schools:
            school = schools.first()
            users = User.objects.filter(school=school)
            if users:
                user = users.first()
                self.stdout.write(f'\nTo login as {user.email}, use one of these formats:')
                self.stdout.write(f'  1. {school.name}/{user.email}')
                self.stdout.write(f'  2. {school.subdomain}/{user.email}')
                self.stdout.write(f'  3. {user.email} (if email is unique)')
