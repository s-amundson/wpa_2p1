import logging
import csv

from celery import shared_task
from .models import Bow
logger = logging.getLogger('inventory')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger(__name__)


@shared_task
def inventory_from_csv():
    celery_logger.warning('inventory')

    with open('inventory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            logger.debug(row['BowID'])
            b = Bow.objects.get_or_create(bow_id=row['BowID'],
                                          defaults={
                                              'hand': row['Hand'],
                                              'poundage': row['Lbs'],
                                              'length': row['Length'],
                                              'type': row['Type'],
                                              'riser_material': row['RiserMaterial'],
                                              'riser_manufacturer': row['Riser Manufacturer'],
                                              'riser_color': row['RiserColor'],
                                              'limb_color': row['LimbColor'],
                                              'limb_manufacturer': row['LimbMan'],
                                              'limb_model': row['LimbModel'],
                                              'in_service': row['InService'] in ['Y', 'y'],
                                              'notes': row['Notes']
                                          })



# BowID,Hand,Lbs,Seq,Length,Type,RiserMaterial,,,,,,,Checkout,InvDate,InvBy,Notes