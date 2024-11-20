import os
import django

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_alert.settings")
django.setup()

# Import your Django models here
from my_api.models import Exercice_configurations, Documents, Contacts
from my_api.Views.Document.alert_config import get_documents_not_validated, process_alerts
from my_api.Utils.test_email import send_simple_email

# Votre fonction de démarrage du cron
def start_cron():
    print("Cron job started.")
    send_simple_email()        
    # get_documents_not_validated()
    process_alerts()
