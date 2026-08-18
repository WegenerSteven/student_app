from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    marks = models.FloatField()
    grade = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate grade based on marks before saving to database
        if self.marks >= 80:
            self.grade = 'A'
        elif self.marks >= 70:
            self.grade = 'B'
        elif self.marks >= 60:
            self.grade = 'C'
        elif self.marks >= 50:
            self.grade = 'D'
        else:
            self.grade = 'Fail'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.grade} ({self.marks}%)"