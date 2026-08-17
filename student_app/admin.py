from django.contrib import admin
from .models import Student
# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'marks', 'grade', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('grade',)
    readonly_fields = ('grade', 'created_at')