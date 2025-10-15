from rest_framework import serializers
from .models import SupportedExportFormat
from diagram.models import Diagram

class ExportDiagramUsingAiSerializer(serializers.Serializer):

    diagram = serializers.UUIDField()
    export_format = serializers.IntegerField()
    
    def validate_export_format(self, value):
        try:
            export_format = SupportedExportFormat.objects.get(id=value)
            return export_format
        except SupportedExportFormat.DoesNotExist:
            raise serializers.ValidationError("Export format not found")
    
    def validate_diagram(self, value):
        try:
            diagram = Diagram.objects.get(id=value)
            return diagram
        except Diagram.DoesNotExist:
            raise serializers.ValidationError("Diagram not found")

class SupportedExportFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedExportFormat
        fields = '__all__'