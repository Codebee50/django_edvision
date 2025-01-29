from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import json
from channels.db import database_sync_to_async

class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        me = self.scope.get('user', None)
        diagram = self.scope.get('diagram', None)
        
        
        if not me.is_anonymous or not diagram:
            self.room_id = f"col_{diagram.id}"
            await self.channel_layer.group_add(
                self.room_id,
                self.channel_name
            )
            await self.accept()
        else:
            raise DenyConnection("User is not authenticated or diagram does not exist")
    
    async def receive(self, text_data=None):
        rd= json.loads(text_data)
        
        user = self.scope['user']
        diagram = self.scope['diagram']
        rd['sender_id'] = str(user.id)
        rd['diagram_id'] = str(diagram.id)
                
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'send.message',
                'text': rd
            }
        )
    
    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['text']))