import asyncio

from .utils import validate_file_upload_data
from .models import EligibleUserUpload, User
from .enums import BulkStatusEnum
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from])
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)


def send_admin_notification_mail(email_data):
    html_template = get_template('emails/admin_notification_mail.html')
    text_template = get_template('emails/admin_notification_mail.txt')
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email(email_data['title'],
               email_data['email'], html_alternative, text_alternative)


def handle_file_upload(data_stream, file_upload: EligibleUserUpload, user: User):
    file, valid_students = validate_file_upload_data(data_stream=data_stream, file_upload=file_upload)

    file_upload.error_file = file
    file_upload.number_of_valid = valid_students
    file_upload.status = BulkStatusEnum.Completed.value
    file_upload.number_of_invalid = file_upload.total_upload - file_upload.number_of_valid
    file_upload.save(update_fields=['number_of_valid', 'number_of_invalid', 'error_file', 'status'])
    email_data = {
        'title': 'Upload Result',
        'email': user.email,
        'subject': ""
    }
    # send_admin_notification_mail(email_data)
    return file_upload
