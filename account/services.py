from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import random
from django.core.cache import cache
from .models import UserAccount
import requests


def send_brevo_email(recipient_email, subject, message):
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.BREVO_API_KEY}", # this is the api key for the brevo api
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY
        },
        json={
            "to": [{"email": recipient_email}],
            "subject": subject,
            "htmlContent": message,
            "sender": {
                "name": "ERDVision",
                "email": "support@erdvision.dev"
            }
        }
    )
    try:
        return response.json()
    except Exception as e:
        print(e)
        return None


def send_raw_email(email, subject, message):
    if settings.DEBUG:
        send_mail(subject, message, f"ERDVision <{settings.DEFAULT_FROM_USER}>", [email])
    else:
        send_brevo_email(email, subject, message)
    # send_mail(subject, message, f"ERDVision <{settings.DEFAULT_FROM_USER}>", [email])


def send_template_email(template, email, subject, **context):
    """Send an email based on a template."""
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    if settings.DEBUG:
        send_mail(subject, plain_message, f"ERDVision <{settings.DEFAULT_FROM_USER}>", [email], html_message=html_message)
    else:
        send_brevo_email(email, subject, html_message)


def generate_code(length=6):
    return "".join([str(random.randint(0, 9)) for i in range(length)])


def send_invite_email(email, diagram, invitation):
    send_template_email(
        "invite.html",
        email,
        "ERDVision collaboration invite",
        **{
            "diagram": diagram,
            "url": f"{settings.FE_URL}/invitation/{invitation.id}/",
            "user_email": email,
        },
    )


def send_password_reset_email(email):
    otp = generate_code()
    cache.set(f"pr-{email}", otp, timeout=500)
    send_raw_email(
        email,
        "ERDVision password reset",
        f"Use this code to reset your ERDVision account password<br><b>{otp}</b><br>Please do not share this code with anyone, it expires in the next 5 minutes.",
    )
    return True


def verify_password_reset_otp(email, user_otp):
    cached_otp = cache.get(f'pr-{email}')
    
    try:
        user = UserAccount.objects.get(email=email)
    except UserAccount.DoesNotExist:
        return False, "Invalid user account"

    if cached_otp and user:
        if user_otp == cached_otp:
            return True, "Valid otp"
        else:
            return False, "Invalid otp"
    return False, "Invalid otp"


def send_verification_email(email):
    otp = generate_code()
    cache.set(f"verf-{email}", otp, timeout=300)
    send_raw_email(
        email,
        "ERDVision account activation",
        f"Your otp verification code is {otp}.\n\nDon't share this code with anyone. It is valid for the next 5 minutes.",
    )


def confirm_verification_email(email: str, otp: str) -> bool:
    cached_otp = cache.get(f"verf-{email}", None)
    return cached_otp == otp


def get_user_by_email(email):
    try:
        user = UserAccount.objects.get(email=email)
    except UserAccount.DoesNotExist:
        return None
    return user
