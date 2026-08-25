import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


def validate_admission_number(value):
    if not re.fullmatch(r"FAC/\d{4}/\d{3}", value):
        raise ValidationError("Use the format FAC/YYYY/NNN.")


class AdmissionNumberSequence(models.Model):
    year = models.PositiveIntegerField(unique=True)
    last_number = models.PositiveIntegerField(default=0)


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    admission_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        validators=[validate_admission_number],
    )
    year_of_study = models.PositiveSmallIntegerField(
        choices=[(year, f"Year {year}") for year in range(1, 5)],
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(
        upload_to="student_profiles/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.admission_number:
            from django.db import transaction
            from django.utils import timezone

            year = timezone.now().year
            prefix = f"FAC/{year}/"

            with transaction.atomic():
                (
                    sequence,
                    _,
                ) = AdmissionNumberSequence.objects.select_for_update().get_or_create(
                    year=year
                )

                existing_numbers = Student.objects.filter(
                    admission_number__startswith=prefix
                ).exclude(pk=self.pk)

                highest_existing = 0

                for admission_number in existing_numbers.values_list(
                    "admission_number",
                    flat=True,
                ):
                    try:
                        number = int(admission_number.rsplit("/", 1)[1])
                        highest_existing = max(highest_existing, number)
                    except (IndexError, ValueError):
                        continue

                sequence.last_number = (
                    max(
                        sequence.last_number,
                        highest_existing,
                    )
                    + 1
                )

                sequence.save(update_fields=["last_number"])

                self.admission_number = f"FAC/{year}/{sequence.last_number:03d}"
        super().save(*args, **kwargs)

    @property
    def name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    marks = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course",
            )
        ]

    @property
    def grade(self):
        if self.marks >= 80:
            return "A"
        if self.marks >= 70:
            return "B"
        if self.marks >= 60:
            return "C"
        if self.marks >= 50:
            return "D"
        return "Fail"

    def __str__(self):
        return f"{self.student} - {self.course}"
