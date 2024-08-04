"""
import os
import django
from apscheduler.schedulers.blocking import BlockingScheduler

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_alert.settings")
django.setup()

# Import your Django models here
from my_api.Views.Document.alert_config import getDocumentNotValidate

# Votre fonction de démarrage du cron
def start_cron():
    getDocumentNotValidate()
    print("Cron job started.")

# Configurer le scheduler
scheduler = BlockingScheduler()
scheduler.add_job(start_cron, 'interval', days=1)

try:
    print("Starting scheduler...")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass

"""