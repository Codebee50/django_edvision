from rest_framework import generics
from .overhaul_serializers import DiagramOverhaulSerializer

class OverHaulDiagramView(generics.GenericAPIView):
    serializer_class= DiagramOverhaulSerializer
    def post(self, request, *args, **kwargs):
        pass