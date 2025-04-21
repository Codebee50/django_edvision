from account.models import Notification
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated


def notify_user(user, title, description):
    return Notification.objects.create(user=user, title=title, description=description)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, NotAuthenticated):
        response.data = {'detail': 'Please signup or login to proceed.'}
    
    return response