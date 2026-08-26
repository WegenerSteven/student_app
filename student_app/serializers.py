from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description']

class EnrollmentSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.name')
    grade = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_name', 'marks', 'grade']

    def validate_marks(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Marks must be between 0 and 100.")
        return value

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'name', 'email', 
            'year_of_study', 'phone', 'is_active', 
            'profile_photo', 'created_at', 'enrollments'
        ]
        read_only_fields = ['id', 'admission_number', 'created_at']
        