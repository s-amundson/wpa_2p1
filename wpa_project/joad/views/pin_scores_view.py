from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ..forms import PinScoresForm
from ..models import PinScores
from src.mixin import BoardMixin


class PinScoreListView(BoardMixin, ListView):
    model = PinScores
    template_name = 'joad/pin_scores.html'


class PinScoreView(BoardMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = PinScoresForm
    success_url = reverse_lazy('joad:pin_score_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Pin Score'
        return context

    def get_form(self):
        sid = self.kwargs.get("score_id", None)
        if sid is not None:
            form = self.form_class(instance=get_object_or_404(PinScores, pk=sid),
                                   **self.get_form_kwargs())
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
