from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import random
from django.core.cache import cache
from .models import UserAccount

def send_raw_email(email, subject, message):
    send_mail(subject, message, f"ERDVision <{settings.DEFAULT_FROM_USER}>", [email])

def send_template_email(template, email, subject, **context):
    """Send an email based on a template."""
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        f"ERDVision <{settings.DEFAULT_FROM_USER}>",
        [email],
        html_message=html_message,
    )


def generate_code(length=6):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def send_invite_email(email, diagram, invitation):
    send_template_email('invite.html', email, "ERDVision collaboration invite", **{
        'diagram': diagram,
        'url': f"{settings.FE_URL}/invitation/{invitation.id}/",
        "user_email": email
    })


def send_verification_email(email):
    otp = generate_code()
    cache.set(f"verf-{email}", otp, timeout=300)
    send_raw_email(email, 'ERDVision account activation', f"Your otp verification code is {otp}. Don't share this code with anyone. It is valid for the next 5 minutes.0")
    
def confirm_verification_email(email:str, otp:str)->bool:
    cached_otp = cache.get(f"verf-{email}", None)
    return cached_otp == otp

def get_user_by_email(email):
    try:
        user= UserAccount.objects.get(email=email)
    except UserAccount.DoesNotExist:
        return None
    return user