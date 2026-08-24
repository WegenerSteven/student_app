from django.contrib import admin

from .models import Student, Course, Enrollment


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    readonly_fields = ("created_at",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "marks", "grade")
    list_filter = ("course",)
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "course__name",
    )
