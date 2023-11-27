import logging
from celery import shared_task
from ecomapp.models import Customer

logger = logging.getLogger(__name__)

@shared_task(blind=True)
def delete_all_secret_keys():
    logger.info("Deleting secret keys for customers")
    try:
        customers_with_secret_keys = Customer.objects.exclude(secret_key__isnull=True).exclude(secret_key='')
        deleted_count = customers_with_secret_keys.update(secret_key=None)
        logger.info(f"Deleted secret keys for {deleted_count} customers")
    except Exception as e:
        logger.exception(f"Failed to delete secret keys: {e}")
