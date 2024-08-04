from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class MailConfig:
    def sendResetPasswordEmail(email, password, user):
        """
        Envoyer un email contenant le nouveau mot de passe à l'utilisateur
        """
        subject = 'Votre identifiant'
        recipient_list = [email]
        context = {'password': password, 'email': email, 'subject':subject, 'user': user}
        html_message = render_to_string('email_template.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        except Exception as e:
            print(f"Error sending email: {e}")

    def sendDocumentEmail(recipient_list, subject, message):
        context = {'subject':subject, 'message': message}
        email_message = render_to_string('relance_template.html', context)
        plain_message = strip_tags(email_message)

        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=email_message)
        except Exception as e:
            print(f"Error sending email: {e}")