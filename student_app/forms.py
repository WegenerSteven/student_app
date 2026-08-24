from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student, Course, Enrollment


class CustomUserCreationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "First name"}),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Surname"}),
    )
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
            "phone",
            "courses",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            student = Student.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
            )

            student.enrollments.bulk_create(
                [
                    self._enrollment_model(student=student, course=course)
                    for course in self.cleaned_data["courses"]
                ]
            )
        return user

    @property
    def _enrollment_model(self):
        from .models import Enrollment

        return Enrollment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        # Exclude grade because it is computed automatically in models.py save()
        fields = ["user", "phone"]

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Student").distinct()
    )


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["marks"]

    # Custom field validation for marks
    def clean_marks(self):
        marks = self.cleaned_data.get("marks")
        if marks < 0 or marks > 100:
            raise forms.ValidationError("Marks must be between 0 and 100.")
        return marks
