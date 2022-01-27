from django.utils import timezone


class StudentHelper:
    def calculate_age(self, born, target_date=timezone.now().date()):
        return target_date.year - born.year - ((target_date.month, target_date.day) < (born.month, born.day))
