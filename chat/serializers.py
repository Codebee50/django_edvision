from rest_framework import serializers
from .models import ChatMessage
from account.serializers import UserSerializer

class ChatMessageSerializer(serializers.ModelSerializer):
    sender= UserSerializer()
    
    class Meta:
        model = ChatMessage
        fields = '__all__'