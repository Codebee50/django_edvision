from account.models import Notification
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated

from account.services import send_raw_email


def notify_user(user, title, description, send_email=False):
    notification = Notification.objects.create(user=user, title=title, description=description)
    if send_email:
        send_raw_email(user.email, title, description)
    return notification

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, NotAuthenticated):
        response.data = {'detail': 'Please signup or login to proceed.'}
    
    return response