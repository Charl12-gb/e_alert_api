from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from my_api.models import Exercice_configurations, Documents, Contacts

def verifyConfigurations(document, config):
    days_difference = (document.deadline - timezone.now().date()).days

    serialized_number_day_sends = data.get('number_day_send', '')
    number_day_sends = serialized_number_day_sends.split(',') if serialized_number_day_sends else []
    number_day_sends = [int(day) for day in number_day_sends]

    if config.moment == 'Before' and days_difference in number_day_sends:
        return document
    elif config.moment == 'After' and -days_difference in number_day_sends:
        return document
    return None


def sendAlertNotifications(document, recipient_emails, config):
    subject = 'ALERTE DOCUMENT : ' + document.name

    context = {'document': document, 'title': config.name, 'message': config.content_mail}
    email_message = render_to_string('alert_template.html', context)
    plain_message = strip_tags(email_message)

    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, plain_message, from_email, recipient_emails, html_message=email_message)

def getDocumentNotValidate():
    not_validated_documents = Documents.objects.filter(~Q(status='Validated'))

    for document in not_validated_documents:
        configs = Exercice_configurations.objects.filter(document=document)

        for config in configs:
            contact_ids = [int(id_str) for id_str in config.emails.split(',') if id_str.strip().isdigit()]
            partner_contacts = Contacts.objects.filter(id__in=contact_ids)
            recipient_emails = [contact.email for contact in partner_contacts]

            if config.send_mail_to_partner:
                try:
                    partner = Users.objects.get(id=document.partner_id)
                    recipient_emails.append(partner.email)
                except Users.DoesNotExist:
                    pass 

            validated_document = verifyConfigurations(document, config)
            if validated_document:
                sendAlertNotifications(validated_document, recipient_emails, config)
