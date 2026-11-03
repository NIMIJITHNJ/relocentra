from django.urls import path
from .views import assignment_view

urlpatterns = [
    path("", assignment_view, name="assignment"),
]
