from django.core.mail import send_mail
from django.conf import settings

def send_email_verify(email, token):
    subject = 'Xác nhận email để tạo tài khoản'
    message = f'Mã xác nhận tài khoản của bạn là {token}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail(subject, message, email_from, recipient_list)
    return True