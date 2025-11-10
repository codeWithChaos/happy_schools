"""
Management command to initialize school data with Ghanaian education system classes.
Usage: python manage.py init_school_data <school_id>
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date
from apps.accounts.models import School, AcademicYear, Class, Section


class Command(BaseCommand):
    help = 'Initialize school data with Ghanaian education system classes and sections'

    def add_arguments(self, parser):
        parser.add_argument(
            'school_id',
            type=int,
            help='School ID to initialize data for'
        )
        parser.add_argument(
            '--year',
            type=str,
            default=f'{date.today().year}-{date.today().year + 1}',
            help='Academic year (e.g., 2024-2025)'
        )

    def handle(self, *args, **options):
        school_id = options['school_id']
        year = options['year']
        
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            raise CommandError(f'School with ID {school_id} does not exist')
        
        self.stdout.write(self.style.SUCCESS(f'Initializing data for school: {school.name}'))
        
        # Create Academic Year
        academic_year, created = AcademicYear.objects.get_or_create(
            school=school,
            year=year,
            defaults={
                'start_date': date(date.today().year, 9, 1),  # September 1st
                'end_date': date(date.today().year + 1, 7, 31),  # July 31st next year
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created academic year: {year}'))
        else:
            self.stdout.write(self.style.WARNING(f'Academic year {year} already exists'))
        
        # Ghanaian Education System Classes
        ghanaian_classes = [
            'Creche',
            'Nursery',
            'Kindergarten 1',
            'Kindergarten 2',
            'Class 1',
            'Class 2',
            'Class 3',
            'Class 4',
            'Class 5',
            'Class 6',
            'JHS 1',
            'JHS 2',
            'JHS 3',
        ]
        
        # Standard sections for each class
        sections = ['A', 'B', 'C']
        
        classes_created = 0
        sections_created = 0
        
        for class_name in ghanaian_classes:
            # Create or get the class
            class_obj, class_created = Class.objects.get_or_create(
                school=school,
                academic_year=academic_year,
                name=class_name,
                defaults={
                    'description': f'{class_name} for academic year {year}',
                    'is_active': True
                }
            )
            
            if class_created:
                classes_created += 1
                self.stdout.write(f'  Created class: {class_name}')
            
            # Create sections for this class
            for section_name in sections:
                section_obj, section_created = Section.objects.get_or_create(
                    class_obj=class_obj,
                    name=section_name,
                    defaults={
                        'capacity': 30,
                        'is_active': True
                    }
                )
                
                if section_created:
                    sections_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\nInitialization complete!'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Classes created: {classes_created}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Sections created: {sections_created}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'\nYou can now add students to classes and sections.'
        ))
