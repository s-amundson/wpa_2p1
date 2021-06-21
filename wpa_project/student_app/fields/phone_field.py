import logging

from django.db import models
import phonenumbers
logger = logging.getLogger(__name__)

# TODO: format output string for templates - not sure where to perform formatting
class PhoneField(models.CharField):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = 31
        description = "String to hold phone number"

    def to_python(self, value):
        if isinstance(value, str):
            n = phonenumbers.parse(value, 'US')
            s = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
            # logging.debug(f'n = {n}, s = {s}')
            return s
        if value is None:
            return value

    # def value_to_string(self, obj):
    #     value = self.value_from_object(obj)
    #     n = phonenumbers.format_number(value, phonenumbers.PhoneNumberFormat.NATIONAL)
    #     logging.debug(f'unformatted phone number: {value}, formatted: n')
    #     return n
