import os

from celery import Celery


from settings.conf import ENV_ID


os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

app = Celery("marketplace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
