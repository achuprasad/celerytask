from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomproject.settings')

app = Celery('ecomproject')

# Use broker_connection_retry_on_startup for retrying connections on startup
app.conf.enable_utc = True
app.conf.update(timezone ='Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'run-task-every-evening': {
        'task': 'ecomapp.tasks.delete_all_secret_keys',  
        'schedule': 10.0,  
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
