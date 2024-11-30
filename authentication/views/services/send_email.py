from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail


def send_email(email: str, link: str, subject: str, template_name: str, username: str):
    context = {
        "username": username,
        "link": link
    }
    try:
        send_mail(
            subject=subject,
            message=str(context),
            html_message=render_to_string(
                template_name=template_name,
                context=context
            ),
            from_email=None,
            recipient_list=[email]
        )
    except SMTPException as e:
        print("ERROR sending email", str(e))
        # logger.error(str(e))
