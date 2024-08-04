import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_alert.settings")
django.setup()

# Maintenant, vous pouvez importer vos modèles Django
from my_api.models import Exercice_configurations, Documents, Contacts

# Votre fonction de démarrage du cron
def start_cron():
    from my_api.my_views.alert_config import getDocumentNotValidate
    getDocumentNotValidate()
    print("Cron job started.")
