from django.contrib.auth.mixins import UserPassesTestMixin

class BoardMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        return False