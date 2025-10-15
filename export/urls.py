from .import views
from django.urls import path

urlpatterns = [
    path('script/<uuid:diagram_id>/', views.ExportPostgresView.as_view(), name='export-postgres'),
    path('formats/', views.GetSupportedExportFormats.as_view(), name='get-supported-export-formats'),
    path('ai/<uuid:diagram_id>/<int:export_format_id>/', views.ExportDiagramUsingAi.as_view(), name='export-diagram-using-ai'),
]