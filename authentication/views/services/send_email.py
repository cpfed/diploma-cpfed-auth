from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
import django.core.mail


def send_emails(emails: list[str], subject: str, html_message: str):
    try:
        django.core.mail.send_mail(
            subject=subject,
            message="",
            html_message=html_message,
            from_email=None,
            recipient_list=emails
        )
    except SMTPException as e:
        print("ERROR sending email", str(e))
        return e
        # logger.error(str(e))
    except Exception as e:
        print("ERROR sending email", str(e))


def send_email_with_context(email: str, subject: str, template_name: str, context: dict):
    return send_emails([email], subject, render_to_string(
        template_name=template_name,
        context=context
    ))
