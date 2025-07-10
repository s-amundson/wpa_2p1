from django.db import models

import logging
logger = logging.getLogger(__name__)

class BowManager(models.Manager):
    def last_bow(self, hand, pounds):
        return self.filter(hand=hand, poundage=pounds).order_by('-poundage').last()

    def next_id(self, hand, pounds):
        last = self.last_bow(hand, pounds)
        if not last:
            return 1
        else:
            logger.debug(int(last.bow_id[-2:]))
            return int(last.bow_id[-2:]) + 1


class Bow(models.Model):
    HAND_CHOICES = {'R': 'Right', 'L': 'Left', 'A': 'Ambidextrous'}
    BOW_TYPES = {'TDR': 'Take Down Recurve', '1PC': 'One Piece', 'CPD': 'Compound'}

    bow_id = models.CharField(max_length=40)
    hand = models.CharField(max_length=20, choices=HAND_CHOICES)
    poundage = models.IntegerField()
    length = models.IntegerField()
    type = models.CharField(max_length=10, choices=BOW_TYPES)
    riser_material = models.CharField(max_length=40, choices={'plastic': 'Plastic', 'wood': 'Wood', 'rubber': 'Rubber'})
    riser_manufacturer = models.CharField(max_length=40)
    riser_color = models.CharField(max_length=20)
    limb_color = models.CharField(max_length=20)
    limb_manufacturer = models.CharField(max_length=40)
    limb_model = models.CharField(max_length=20)
    in_service = models.BooleanField(default=True)
    # is_youth = models.BooleanField(default=False)
    added_date = models.DateTimeField(auto_now_add=True)
    # notes = models.TextField()

    objects = BowManager()
    def last_inventory(self):
        return self.bowinventory_set.all().order_by('-inventory_date').first()

class BowInventory(models.Model):
    bow = models.ForeignKey(Bow, on_delete=models.CASCADE)
    inventory_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('student_app.User', on_delete=models.PROTECT)