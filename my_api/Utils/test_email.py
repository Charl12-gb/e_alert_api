from django.core.mail import send_mail
from django.conf import settings

def send_simple_email():
    subject = 'Confirmation cron'
    message = 'Les messages cron ont été envoyés avec succès'
    recipient_list = ['gboyoucharles.tech@gmail.com']
    email_from = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, email_from, recipient_list)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
