from rest_framework import generics
from diagram.models import Diagram
from common.responses import ErrorResponse, SuccessResponse
from .postgresql import export_postgres
import os
from django.conf import settings
from .utils import write_destination
from diagram.choices import DatabaseTypeChoices
from django.http import FileResponse, HttpResponse
# Create your views here.


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

        
        return ErrorResponse(message=f"Scripts export for {diagram.database_type} is not yet supported.")
        
        