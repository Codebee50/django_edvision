from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import json
from channels.db import database_sync_to_async
from .models import ChatMessage
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        me = self.scope.get('user',None)
        diagram = self.scope.get('diagram', None)
        
        if not me.is_anonymous or not diagram:
            self.room_id = f"room_{diagram.id}"
            await self.channel_layer.group_add(
                self.room_id,
                self.channel_name
            )
            await self.accept()
        else:
            raise DenyConnection("User is not authenticated or diagram does not exist")
    
    
    async def receive(self, text_data=None):
        rd = json.loads(text_data)
        action = rd.get('action', None)
        
        user = self.scope['user']
        diagram = self.scope['diagram']
        
        if action == 'chat_message':
            message = rd.get('message_body')

            created_message = await self.create_chat_message(message)
            if created_message:
                ws_response = {
                    'message_body': message,
                    'sender_id': str(user.id),
                    'timestamp': timezone.now().isoformat(),
                    'created_message_id': getattr(created_message, 'id', None),
                    'action': 're_message',
                    'sender_name': f"{user.first_name}{user.last_name}",
                    'profile_url': getattr(user, 'profile_photo', None)
                }
                
                await self.channel_layer.group_send(
                    f"room_{diagram.id}",
                    {
                        'type': 'chat.message',
                        'text': ws_response
                    }
                )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['text']))
    
    @database_sync_to_async
    def create_chat_message(self, message):
        sender = self.scope.get('user')
        diagram = self.scope.get('diagram')
        
        chat_message, message = ChatMessage.chatm.create_chat(diagram, sender, message)
        return chat_message