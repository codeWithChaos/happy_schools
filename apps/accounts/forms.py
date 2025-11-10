"""
Forms for the accounts app.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.text import slugify
from .models import School, User


class SchoolLoginForm(AuthenticationForm):
    """
    Custom login form that supports school-based authentication.
    Users can login using: school_name/email or school_name/username
    """
    username = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-0 py-2 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6',
            'placeholder': 'School Name/Email or Email',
            'autocomplete': 'username'
        }),
        label='School Name / Email',
        help_text='Enter your school name followed by your email (e.g., "Happy Academy/john@example.com") or just your email'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full rounded-md border-0 py-2 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        }),
        label='Password'
    )
    
    error_messages = {
        'invalid_login': (
            "Please enter a correct school name/email and password. "
            "Note that both fields may be case-sensitive. "
            "Format: SchoolName/Email (e.g., 'Happy Academy/john@example.com')"
        ),
        'inactive': "This account is inactive.",
    }


class SchoolRegistrationForm(forms.ModelForm):
    """
    Form for school registration.
    Creates a new school and its admin user.
    """
    # School fields
    school_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'e.g., Springfield High School'
        }),
        label='School Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'school@example.com'
        }),
        label='School Email'
    )
    
    phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': '+1234567890'
        }),
        label='School Phone'
    )
    
    address_line1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'Street Address'
        }),
        label='Address Line 1'
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'City'
        }),
        label='City'
    )
    
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'State/Province'
        }),
        label='State/Province'
    )
    
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'Postal Code'
        }),
        label='Postal Code'
    )
    
    # Admin user fields
    admin_first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'John'
        }),
        label='Admin First Name'
    )
    
    admin_last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'Doe'
        }),
        label='Admin Last Name'
    )
    
    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': 'admin@example.com'
        }),
        label='Admin Email'
    )
    
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': '••••••••'
        }),
        label='Admin Password',
        help_text='Password must be at least 8 characters long'
    )
    
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
            'placeholder': '••••••••'
        }),
        label='Confirm Password'
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'
        }),
        label='I agree to the Terms of Service and Privacy Policy'
    )
    
    class Meta:
        model = School
        fields = ['school_name', 'email', 'phone', 'address_line1', 'city', 'state', 'postal_code']
    
    def clean_school_name(self):
        """Validate and generate subdomain from school name"""
        school_name = self.cleaned_data['school_name']
        subdomain = slugify(school_name)
        
        # Check if subdomain is unique
        if School.objects.filter(subdomain=subdomain).exists():
            raise forms.ValidationError('A school with this name already exists. Please choose a different name.')
        
        return school_name
    
    def clean_admin_email(self):
        """Check if admin email is unique"""
        admin_email = self.cleaned_data['admin_email']
        
        if User.objects.filter(email=admin_email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email.')
        
        return admin_email
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        password_confirm = cleaned_data.get('admin_password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match.')
        
        if password and len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Create school and admin user"""
        from datetime import date
        
        # Create school
        school = super().save(commit=False)
        school.name = self.cleaned_data['school_name']
        school.subdomain = slugify(self.cleaned_data['school_name'])
        school.email = self.cleaned_data['email']
        school.phone = self.cleaned_data['phone']
        school.address_line1 = self.cleaned_data['address_line1']
        school.city = self.cleaned_data['city']
        school.state = self.cleaned_data['state']
        school.postal_code = self.cleaned_data['postal_code']
        school.subscription_status = 'trial'
        school.is_active = True
        
        if commit:
            school.save()
            
            # Create admin user
            admin_user = User.objects.create_user(
                username=self.cleaned_data['admin_email'],  # Use email as username
                email=self.cleaned_data['admin_email'],
                password=self.cleaned_data['admin_password'],
                first_name=self.cleaned_data['admin_first_name'],
                last_name=self.cleaned_data['admin_last_name'],
                role='admin',
                school=school,
                is_active=True
            )
            
            # Initialize school with Ghanaian education system classes
            self._initialize_school_data(school)
        
        return school
    
    def _initialize_school_data(self, school):
        """Initialize school with academic year, classes, and sections"""
        from datetime import date
        from .models import AcademicYear, Class, Section
        
        # Create Academic Year
        current_year = date.today().year
        academic_year = AcademicYear.objects.create(
            school=school,
            year=f'{current_year}-{current_year + 1}',
            start_date=date(current_year, 9, 1),
            end_date=date(current_year + 1, 7, 31),
            is_active=True
        )
        
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
        
        for class_name in ghanaian_classes:
            # Create the class
            class_obj = Class.objects.create(
                school=school,
                academic_year=academic_year,
                name=class_name,
                description=f'{class_name} for academic year {academic_year.year}',
                is_active=True
            )
            
            # Create sections for this class
            for section_name in sections:
                Section.objects.create(
                    class_obj=class_obj,
                    name=section_name,
                    capacity=30,
                    is_active=True
                )

