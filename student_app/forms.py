from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student

class CustomUserCreationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Surname'
        })
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )

    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        )
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        # Exclude grade because it is computed automatically in models.py save()
        fields = ['name', 'email', 'phone', 'marks']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +254 700 000000'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0 - 100', 'min': '0', 'max': '100'}),
        }

    # Custom field validation for marks
    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        if marks < 0 or marks > 100:
            raise forms.ValidationError("Marks must be between 0 and 100.")
        return marks