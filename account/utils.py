from account.models import Notification


def notify_user(user, title, description):
    return Notification.objects.create(user=user, title=title, description=description)