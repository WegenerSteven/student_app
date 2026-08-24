from django.urls import path

from . import views

app_name = "student_app"

urlpatterns = [
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
]
