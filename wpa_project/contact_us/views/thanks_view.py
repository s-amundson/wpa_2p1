from django.views.generic import TemplateView


class ThanksView(TemplateView):
    template_name = 'student_app/message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['message'] = 'Thanks for contacting us.'
        return context