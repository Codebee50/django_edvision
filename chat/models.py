from django.db import models
from diagram.models import Diagram
from account.models import UserAccount

# Create your models here.

class ChatManager(models.Manager):
    def create_chat(self, diagram, sender, message, commit=True):
        try:
            obj = self.model(
                diagram=diagram,
                sender=sender,
                message =message
            )
            if commit:
                obj.save()
            return obj, 'chat_created'
        except:
            return None, "Error creating chat"



class ChatMessage(models.Model):
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    message = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = models.Manager()
    chatm = ChatManager()
    