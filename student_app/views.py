from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import StudentSerializer, CourseSerializer, EnrollmentSerializer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from functools import wraps

from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404, redirect, render

from django.db import transaction
from django.db.models import Q

from .forms import AdminStudentCreationForm, CustomUserCreationForm, EnrollmentForm
from .models import Student, Enrollment, Course


# Authorization helpers
def is_admin(user):
    return user.is_staff or user.is_superuser


def is_teacher(user):
    return user.groups.filter(name="Teacher").exists()


def is_student(user):
    return user.groups.filter(name="Student").exists()


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not is_admin(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


def teacher_or_admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not (is_admin(request.user) or is_teacher(request.user)):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


# REGISTRATION VIEW
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                student_group, _ = Group.objects.get_or_create(name="Student")
                user.groups.add(student_group)

            messages.success(request, f"Registration successful. Your admission number is {user.student_profile.admission_number}")
            return redirect("login")
    else:
        form = CustomUserCreationForm(
            request.POST,
            request.FILES,
        )

    return render(request, "registration/register.html", {"form": form})


# 1. LIST VIEW (With Search)
@login_required
def student_list(request):
    if is_student(request.user):
        return redirect(
            "student_app:detail",
            pk=request.user.student_profile.pk,
        )

    query = request.GET.get("q", "")
    students = Student.objects.select_related("user").order_by("-created_at")

    if query:
        students = Student.objects.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(admission_number__icontains=query)
        )

    return render(
        request,
        "student_app/student_list.html",
        {
            "students": students,
            "query": query,
            "can_add": is_admin(request.user),
            "can_edit_marks": is_admin(request.user) or is_teacher(request.user),
            "can_delete": is_admin(request.user),
        },
    )


# 2. DETAIL VIEW
@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related("user"), pk=pk)

    if is_student(request.user) and student.user_id != request.user.id:
        raise PermissionDenied

    enrollments = student.enrollments.select_related("course")

    return render(
        request,
        "student_app/student_detail.html",
        {
            "student": student,
            "enrollments": enrollments,
            "can_edit_marks": is_admin(request.user) or is_teacher(request.user),
            "can_delete": is_admin(request.user),
        },
    )


# 3. CREATE VIEW
@admin_required
def student_add(request):
    if request.method == "POST":
        form = AdminStudentCreationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student '{student.name}' was added with admission number "
                f"{student.admission_number}.",
            )
            return redirect("student_app:list")
    else:
        form = AdminStudentCreationForm()

    return render(
        request,
        "student_app/student_form.html",
        {
            "form": form,
            "title": "Add New Student",
            "button_text": "Save Student",
        },
    )


# 4. UPDATE VIEW
# @admin_required
# def student_edit(request, pk):
#     student = get_object_or_404(Student.objects.select_related("user"), pk=pk)

#     if request.method == "POST":
#         form = StudentForm(request.POST, instance=student)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request, f"Student '{student.name}' was successfully updated!"
#             )
#             return redirect("student_app:detail", pk=student.pk)
#     else:
#         form = StudentForm(instance=student)

#     return render(
#         request,
#         "student_app/student_form.html",
#         {
#             "form": form,
#             "student": student,
#             "title": f"Edit Student: {student.name}",
#             "button_text": "Update Student",
#         },
#     )


@teacher_or_admin_required
def enrollment_edit(request, pk):
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        pk=pk,
    )

    if request.method == "POST":
        form = EnrollmentForm(request.POST, instance=enrollment)

        if form.is_valid():
            if hasattr(form, "warning"):
                messages.warning(request, form.warning)
            form.save()
            messages.success(request, "Marks updated successfully.")
            return redirect(
                "student_app:detail",
                pk=enrollment.student.pk,
            )
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(
        request,
        "student_app/student_form.html",
        {
            "form": form,
            "title": f"Edit Marks: {enrollment.course.name}",
            "button_text": "Save Marks",
        },
    )


# 5. DELETE VIEW
@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.name
        student.delete()
        messages.success(request, f"Student '{name}' was deleted.")
        return redirect("student_app:list")

    return render(
        request, "student_app/student_confirm_delete.html", {"student": student}
    )


def home(request):
    return render(request, "home.html")

# ─── DRF AUTHENTICATION ENDPOINTS ───────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_staff': user.is_staff,
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

# ─── DRF VIEWSETS ───────────────────────────────────
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user').all().order_by('-created_at')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year_of_study', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'admission_number']
    ordering_fields = ['created_at', 'year_of_study']

    # GET /api/students/stats/
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_students = Student.objects.count()
        avg_marks = Enrollment.objects.aggregate(avg=Avg('marks'))['avg'] or 0
        pass_count = Enrollment.objects.filter(marks__gte=50).values('student').distinct().count()
        fail_count = Enrollment.objects.filter(marks__lt=50).values('student').distinct().count()

        return Response({
            'total_students': total_students,
            'average_marks': round(avg_marks, 2),
            'pass_count': pass_count,
            'fail_count': fail_count,
        })

    # POST /api/students/{id}/deactivate/
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response({'status': f'Student {student.admission_number} deactivated'}, status=status.HTTP_200_OK)