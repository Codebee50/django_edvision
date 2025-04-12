from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.GetPlans.as_view(), name='get-plans-list')
]