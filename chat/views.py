from django.shortcuts import render
from rest_framework import generics
from .serializers import ChatMessageSerializer
from .models import ChatMessage
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class GetDiagramMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        diagram_id = self.kwargs.get('diagram_id')
        return ChatMessage.objects.filter(diagram__id=diagram_id)