from rest_framework import generics
from diagram.models import Diagram
from common.responses import ErrorResponse, SuccessResponse
from .postgresql import export_postgres
from .djangoorm import export_django
from .agents import export_diagram_using_claude
import os
from django.conf import settings
from .utils import write_destination
from diagram.choices import DatabaseTypeChoices
from django.http import FileResponse, HttpResponse
from .models import SupportedExportFormat
from .serializers import SupportedExportFormatSerializer, ExportDiagramUsingAiSerializer
from rest_framework.permissions import IsAuthenticated
from common.utils import format_first_error
# Create your views here.


class GetSupportedExportFormats(generics.ListAPIView):
    serializer_class = SupportedExportFormatSerializer
    queryset = SupportedExportFormat.objects.all()

class ExportDiagramUsingAi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        diagram_id = kwargs.get('diagram_id')
        export_format_id = kwargs.get('export_format_id')
        try:
            diagram = Diagram.objects.get(id=diagram_id)
        except Diagram.DoesNotExist:
            return ErrorResponse(message="Diagram not found")
        try:
            export_format = SupportedExportFormat.objects.get(id=export_format_id)
        except SupportedExportFormat.DoesNotExist:
            return ErrorResponse(message="Export format not found")
        
        success,response = export_diagram_using_claude(diagram_id=str(diagram.id), format_name=export_format.name)
        if not success:
            return ErrorResponse(message="Failed to export diagram", status=500)
        
        file_name= f"erdvision-{export_format.name.replace(' ', '-')}-{diagram.id}{export_format.extension}"
        response = HttpResponse(response, content_type=f'application/{export_format.extension.replace(".", "")}')
        response['Content-Disposition'] = f'filename={file_name}'
        return response        



class ExportPostgresView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        diagram_id = kwargs.get('diagram_id')
        try:
            diagram = Diagram.objects.get(id=diagram_id)
        except Diagram.DoesNotExist:
            return ErrorResponse(message="Diagram not found")
        
        if diagram.database_type == DatabaseTypeChoices.POSTGRESQL:
            statement = export_postgres(diagram=diagram)
            file_name = f"erdvision-pgsql-{diagram.id}.sql"
            response = HttpResponse(statement, content_type="application/sql")
            response['Content-Disposition'] = f'filename={file_name}'
            return response
        if diagram.database_type == DatabaseTypeChoices.DJANGO_ORM:
            statement = export_django(diagram=diagram)
            file_name = f"erdvison-dorm-{diagram.id}.py"
            response = HttpResponse(statement, content_type='application/py')
            response['Content-Disposition'] = f"filename={file_name}"
            return response

        
        return ErrorResponse(message=f"Scripts export for {diagram.database_type} is not yet supported.")
        
        