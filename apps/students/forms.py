from django import forms
from django.contrib.auth import get_user_model
from .models import Student
from apps.accounts.models import Class

User = get_user_model()


class StudentForm(forms.ModelForm):
    """Custom form for creating/updating students with user information"""
    
    # User fields
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        help_text='Password for student login account'
    )
    
    # Override to make nationality optional
    nationality = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter nationality (optional)'
        })
    )
    
    class Meta:
        model = Student
        fields = [
            'admission_number', 'gender', 'blood_group',
            'class_assigned', 'roll_number',
            'date_of_admission', 'religion', 'nationality',
            'medical_conditions', 'allergies', 'previous_school',
            'uses_transport', 'transport_route', 'remarks', 'is_active'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'class_assigned': forms.Select(attrs={'class': 'form-select'}),
            'roll_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_admission': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
            'transport_route': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        self.instance_user = kwargs.pop('instance_user', None)
        super().__init__(*args, **kwargs)
        
        # If updating existing student, populate user fields
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            # Make password optional for updates
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Leave blank to keep current password'
        
        # Filter classes by school
        if self.school:
            self.fields['class_assigned'].queryset = Class.objects.filter(school=self.school)
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        # Check if email already exists (exclude current user if updating)
        user_query = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            user_query = user_query.exclude(pk=self.instance.user.pk)
        
        if user_query.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        """Create or update both User and Student objects"""
        student = super().save(commit=False)
        
        # Create or update user
        if self.instance.pk:
            # Updating existing student
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.username = self.cleaned_data['email']  # Use email as username
            
            # Only update password if provided
            password = self.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            if commit:
                user.save()
        else:
            # Creating new student - need to set school!
            if not self.school:
                raise forms.ValidationError('School is required to create a student.')
            
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password'],
                role='student',
                school=self.school  # Set the school!
            )
            student.user = user
        
        if commit:
            student.save()
        
        return student


class StudentUpdateForm(StudentForm):
    """Form for updating students - password is optional"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password optional and add help text
        self.fields['password'].required = False
        self.fields['password'].help_text = 'Leave blank to keep current password'
        self.fields['password'].widget.attrs['placeholder'] = 'Leave blank to keep current'
