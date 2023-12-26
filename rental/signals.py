from django.db.models.signals import post_delete
from django.dispatch import receiver

from base.models import Location
from rental.models import Rental, RentalCategory
from core.settings import LOGGER as logger

logger.warning("rental.signals loaded")


@receiver(post_delete, sender=Rental)
def rentals_delete_listener(sender, instance, **kwargs):
    logger.warning(f"deleted rental: {instance}")
    Location.objects.filter(id=instance.location.id).delete()


@receiver(post_delete, sender=RentalCategory)
def rental_category_delete_listener(sender, instance, **kwargs):
    logger.warning(f"deleted category: {instance.name}")
    RentalCategory.fetch_categories()
    logger.info(f"re-cached rental categories")


post_delete.connect(rentals_delete_listener, sender=Rental)
post_delete.connect(rental_category_delete_listener, sender=RentalCategory)
