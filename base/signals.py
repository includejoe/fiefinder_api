from django.db.models.signals import post_delete
from django.dispatch import receiver

from base.models import Country, Language
from core.settings import LOGGER as logger

logger.warning("base.signals loaded")


@receiver(post_delete, sender=Country)
def countries_delete_listener(sender, instance, **kwargs):
    logger.warning(f"deleted country: {instance.name}")
    Country.fetch_countries()
    logger.info(f"re-cached countries")


@receiver(post_delete, sender=Language)
def languages_delete_listener(sender, instance, **kwargs):
    logger.warning(f"deleted language: {instance.name}")
    Language.fetch_languages()
    logger.info(f"re-cached languages")


post_delete.connect(countries_delete_listener, sender=Country)
post_delete.connect(languages_delete_listener, sender=Language)
