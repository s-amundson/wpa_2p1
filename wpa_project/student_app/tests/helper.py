from ..models import Student

import logging
logger = logging.getLogger(__name__)


def remove_signatures():
    # remove any files we made.
    students = Student.objects.filter(signature__isnull=False)
    for student in students:
        if student.signature:
            student.signature.delete()
        if student.signature_pdf:
            student.signature_pdf.delete()
