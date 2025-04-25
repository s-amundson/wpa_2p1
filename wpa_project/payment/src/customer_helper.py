import uuid
import logging
from square.core.api_error import ApiError

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
        try:
            result = self.client.customers.create(
                idempotency_key=idempotency_key,
                email_address=self.user.email,
            )
            self.customer = Customer.objects.create(
                customer_id=result.customer.id,
                created_at=result.customer.created_at,
                creation_source=result.customer.creation_source,
                updated_at=result.customer.updated_at,
                user=self.user,
                version=result.customer.version
            )
            return self.customer
        except ApiError as e:
            self.handle_error(e, 'customers.create_customer', ik=idempotency_key)
        return None  # pragma: no cover

    def delete_customer(self):
        c = Customer.objects.get(user=self.user)
        try:
            result = self.client.customers.delete(customer_id=c.customer_id)
            return True
        except ApiError as e:
            self.handle_error(e, 'customers.delete_customer')
            return False

    def retrieve_customer(self):
        self.customer = Customer.objects.get(user=self.user)
        try:
            result = self.client.customers.get(customer_id=self.customer.customer_id)

            self.customer.created_at = result.customer.created_at
            self.customer.creation_source = result.customer.creation_source
            self.customer.updated_at = result.customer.updated_at
            self.customer.user = self.user
            self.customer.version = result.customer.version
            return self.customer
        except ApiError as e:
            self.handle_error(e, 'customers.retrieve_customer')
        return None  # pragma: no cover
