import os

from celery import Celery
from celery.schedules import crontab


from settings.conf import ENV_ID


os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

app = Celery("marketplace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "cleanup-expired-tokens-hourly": {
        "task": "apps.users.tasks.cleanup_expired_tokens",
        "schedule": crontab(minute=0),
    },
}
