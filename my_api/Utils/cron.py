import os
import django
import threading
from apscheduler.schedulers.blocking import BlockingScheduler

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_alert.settings")
django.setup()

# Import your Django models here
from my_api.Views.Document.alert_config import getDocumentNotValidate

# Votre fonction de démarrage du cron
def start_cron():
    print("Cron job started.")
    getDocumentNotValidate()

# Fonction pour démarrer le scheduler dans un thread
def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(start_cron, 'interval', minutes=1)
    scheduler.start()

# Démarrer le scheduler dans un thread
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.start()

# Démarrer le serveur Django
# from django.core.management import execute_from_command_line
# execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
