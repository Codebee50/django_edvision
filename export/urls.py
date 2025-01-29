from .import views
from django.urls import path

urlpatterns = [
    path('script/<uuid:diagram_id>/', views.ExportPostgresView.as_view(), name='export-postgres')
]