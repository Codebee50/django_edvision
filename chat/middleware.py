from channels.db import database_sync_to_async
from account.models import UserAccount
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from diagram.models import Diagram


@database_sync_to_async
def get_user(user_id):
    try: 
        return UserAccount.objects.get(id=user_id)
    except UserAccount.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def get_diagram(diagram_id):
    try:
        return Diagram.objects.get(id=diagram_id)
    except Diagram.DoesNotExist:
        return None
    
class JWTAuthMiddleWare(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()#decode() converts a byte string to a regular string
        query_params = parse_qs(query_string)#passing query string from a url into a dictionary 
        token = query_params.get('token', [None])[0]
        
        diagram_id = query_params.get('did', [None])[0]
        
        # diagram_id = scope['url_route']['kwargs'].get('room_id', None)
        
        if token: 
            try:  
                user_id = UntypedToken(token=token)['user_id']#decodinig the jwt token to get the userid
                scope['user'] = await get_user(user_id)
                scope['diagram'] = await get_diagram(diagram_id)

            except (InvalidToken, TokenError) as e:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)