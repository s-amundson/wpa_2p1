import uuid
import logging

from ..models import Customer
from .square_helper import SquareHelper

logger = logging.getLogger(__name__)


class CustomerHelper(SquareHelper):
    def __init__(self, user):
        super().__init__()
        self.customer = None
        self.user = user

    def create_customer(self):
        idempotency_key = str(uuid.uuid4())
        result = self.client.customers.create_customer(
          body={
            "idempotency_key": idempotency_key,
            "email_address": self.user.email
          }
        )
        if result.is_success():
            # logging.debug(result.body)
            customer = result.body['customer']
            self.customer = Customer.objects.create(
                customer_id=customer['id'],
                created_at=customer['created_at'],
                creation_source=customer['creation_source'],
                updated_at=customer['updated_at'],
                user=self.user,
                version=customer['version']
            )
            return self.customer
        elif result.is_error():  # pragma: no cover
            for error in result.errors:
                self.log_error('N/A', error.get('code', 'unknown_error'), idempotency_key, 'customers.create_customer')
            self.handle_error(result, 'Customer create error')
        return None  # pragma: no cover

    def delete_customer(self):
        c = Customer.objects.get(user=self.user)
        result = self.client.customers.delete_customer(
            customer_id=c.customer_id,
        )

        if result.is_success():
            return True
        elif result.is_error():  # pragma: no cover
            for error in result.errors:
                self.log_error('N/A', error.get('code', 'unknown_error'), None, 'customers.delete_customer')
            self.handle_error(result, 'Customer delete error')
            return False

    def retrieve_customer(self):
        self.customer = Customer.objects.get(user=self.user)
        result = self.client.customers.retrieve_customer(
            customer_id=self.customer.customer_id,
        )

        if result.is_success():
            customer = result.body['customer']
            self.customer.created_at = customer['created_at']
            self.customer.creation_source = customer['creation_source']
            self.customer.updated_at = customer['updated_at']
            self.customer.user = self.user
            self.customer.version = customer['version']
            return self.customer
        elif result.is_error():  # pragma: no cover
            for error in result.errors:
                self.log_error('N/A', error.get('code', 'unknown_error'), None, 'customers.retrieve_customer')
            self.handle_error(result, 'Customer retrieve error')
        return None  # pragma: no cover
