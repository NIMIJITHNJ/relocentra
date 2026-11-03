from django.urls import path
from . import views

urlpatterns = [
    path("", views.immigration_view, name="immigration"),
]
