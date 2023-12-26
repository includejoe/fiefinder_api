from __future__ import absolute_import, unicode_literals

from celery.schedules import crontab
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.conf.broker_url = "redis://localhost:6379/3"
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# use these docs as guide
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html

app.conf.beat_schedule = {
    # "clear_old_notifications": {
    #     "task": "base.tasks.clear_old_notifications",
    #     "schedule": crontab("0", "0", day_of_month="1"),
    # },
    # "check_momo_payment": {
    # "task": "b2c.tasks.check_momo_payment",
    # "schedule": crontab(minute="*/1"),
    # },
}
