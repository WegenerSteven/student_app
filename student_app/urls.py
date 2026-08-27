from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

app_name = "student_app"

router = DefaultRouter()
router.register('api/students', views.StudentViewSet, basename='api-student')
router.register('api/courses', views.CourseViewSet, basename='api-course')
router.register('api/enrollments', views.EnrollmentViewSet, basename='api-enrollment')

urlpatterns = [
    # Web UI Routes
    path("", views.student_list, name="list"),
    path("<int:pk>/", views.student_detail, name="detail"),
    path("add/", views.student_add, name="add"),
    path(
        "enrollment/<int:pk>/edit/",
        views.enrollment_edit,
        name="enrollment_edit",
    ),
    # path("<int:pk>/edit/", views.student_edit, name="edit"),
    path("<int:pk>/delete/", views.student_delete, name="delete"),

    # DRF API Routes
    path("", include(router.urls)),
    path("api/auth/login/", views.api_login, name="api-login"),
    path("api/auth/logout/", views.api_logout, name="api-logout"),
    path("api-auth/", include("rest_framework.urls")),
]
