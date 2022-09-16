from allauth.account.views import LoginView


class LoginView(LoginView):
    template_name = 'account/login_insert.html'
