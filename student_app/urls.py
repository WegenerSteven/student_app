from django.urls import path
from . import views

app_name = "student_app"

urlpatterns = [
    path("", views.student_list, name="list"),
    path("<int:pk>/", views.student_detail, name="detail"),
]
