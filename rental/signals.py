from django.db.models.signals import post_delete
from django.dispatch import receiver

from base.models import Location
from rental.models import Rental
from core.settings import LOGGER as logger

logger.warning("rental.signals loaded")


@receiver(post_delete, sender=Rental)
def rentals_delete_listener(sender, instance, **kwargs):
    logger.warning(f"deleted rental: {instance}")
    Location.objects.filter(id=instance.location.id).delete()


post_delete.connect(rentals_delete_listener, sender=Rental)
