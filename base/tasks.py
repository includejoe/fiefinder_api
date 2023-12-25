import os
import arrow
from celery import shared_task
import firebase_admin
from firebase_admin import credentials, messaging

from base.models import Notification, PushToken
from core.settings import LOGGER as logger

cwd = os.getcwd()
cred_path = os.path.join(cwd, "firebase-adminsdk-keys.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)


@shared_task
def send_notification(data):
    logger.warning("--------------about to send notification --------------------")
    notification = Notification.objects.create(**data)
    if notification.general:
        queryset = PushToken.objects.values_list("fcm_token", flat=True)
        queryset = list(queryset)
    else:
        queryset = notification.recipients

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=notification.title, body=notification.message
            ),
            data=dict(title=notification.title, body=notification.message),
            tokens=queryset,
        )

        response = messaging.send_multicast(message)

        if response.failure_count > 0:
            logger.warning("Some notifications were not sent successfully:")
            for idx, failure in enumerate(response.responses):
                if not failure.success:
                    logger.warning(
                        f"Error sending notifications {idx + 1} with token {message.tokens[idx]}: {failure.exception}"
                    )

        logger.warning("--------------done sending notification --------------------")
    except Exception as e:
        logger.warning(e)
