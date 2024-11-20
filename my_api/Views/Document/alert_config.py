from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from my_api.models import Exercice_configurations, Documents, Contacts, Users

def verify_configurations(document, config):
    days_difference = (document.deadline - timezone.now().date()).days

    serialized_number_day_sends = config.number_day_send or ""
    number_day_sends = [
        int(day) for day in serialized_number_day_sends.split(",") if day.strip().isdigit()
    ]

    if config.moment == 'Before' and days_difference in number_day_sends:
        return True
    elif config.moment == 'After' and -days_difference in number_day_sends:
        return True
    return False

def send_alert_notifications(document, recipient_emails, config):
    subject = f"ALERTE DOCUMENT : {document.name}"

    context = {
        'document': document,
        'title': config.name,
        'message': config.content_mail,
    }
    email_message = render_to_string('alert_template.html', context)
    plain_message = strip_tags(email_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject, plain_message, from_email, recipient_emails, html_message=email_message
        )
    except Exception as e:
        print(f"Error sending email: {e}")

def get_documents_not_validated():
    not_validated_documents = Documents.objects.filter(~Q(status='Validated'))

    for document in not_validated_documents:
        configs = Exercice_configurations.objects.filter(document=document)

        for config in configs:
            recipient_emails = []

            # Fetch partner contact emails
            if config.emails:
                contact_ids = [
                    int(id_str) for id_str in config.emails.split(",") if id_str.strip().isdigit()
                ]
                partner_contacts = Contacts.objects.filter(id__in=contact_ids)
                recipient_emails += [contact.email for contact in partner_contacts]

            # Add partner email if specified
            if config.send_mail_to_partner:
                try:
                    partner = Users.objects.get(id=document.partner_id)
                    recipient_emails.append(partner.email)
                except Users.DoesNotExist:
                    print(f"Partner with ID {document.partner_id} does not exist.")

            # Send email if configuration is valid
            if verify_configurations(document, config):
                send_alert_notifications(document, recipient_emails, config)

def send_email_with_alert(document, alert_level, config):
    """
    Envoie un e-mail avec les détails des documents, receveurs, niveau d'alerte et le titre.
    """
    recipient_emails = ['gboyoucharles.tech@gmail.com']

    subject = f"[{alert_level.upper()}] Alerte : {document.name}"

    context = {
        'document': document,
        'title': config.name,
        'message': config.content_mail,
        'alert_level': alert_level,
        'deadline': document.deadline,
    }

    email_message = render_to_string('alert_me_template.html', context)
    plain_message = strip_tags(email_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject, plain_message, from_email, recipient_emails, html_message=email_message
        )
        print(f"E-mail envoyé avec succès à {recipient_emails}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

def process_alerts():
    """
    Parcourt les documents et configurations pour envoyer des alertes.
    """
    documents = Documents.objects.filter(is_active=True)

    for document in documents:
        configs = Exercice_configurations.objects.filter(document=document)
        for config in configs:
            if verify_configurations(document, config):
                alert_level = config.alert_level
                send_email_with_alert(document, alert_level, config)