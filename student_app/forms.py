from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.db import transaction


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

    year_of_study = forms.ChoiceField(
        choices=[(year, f"Year {year}") for year in range(1, 5)]
    )

    profile_photo = forms.ImageField(required=False)
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
            "year_of_study",
            "profile_photo",
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
                year_of_study=self.cleaned_data["year_of_study"],
                profile_photo=self.cleaned_data.get("profile_photo"),
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


class AdminStudentCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
            "year_of_study",
            "phone",
            "profile_photo",
            "courses",
        ]

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        student_group, _ = Group.objects.get_or_create(name="Student")
        user.groups.add(student_group)

        student = Student.objects.create(
            user=user,
            year_of_study=self.cleaned_data["year_of_study"],
            phone=self.cleaned_data["phone"],
            profile_photo=self.cleaned_data.get("profile_photo"),
        )

        Enrollment.objects.bulk_create(
            [
                Enrollment(student=student, course=course)
                for course in self.cleaned_data["courses"]
            ]
        )

        return student


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

    def clean(self):
        cleaned_data = super().clean()
        marks = cleaned_data.get("marks")
        year = self.instance.student.year_of_study

        if year == 4 and marks is not None and marks < 40:
            self.warning = "Warning: Year 4 marks are below 40."

        return cleaned_data
