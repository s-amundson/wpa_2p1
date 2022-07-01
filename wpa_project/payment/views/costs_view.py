# import logging
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.shortcuts import render
# from django.http import HttpResponseForbidden
# from django.views.generic.base import View
# from django.shortcuts import get_object_or_404
#
# from ..forms import CostsForm
# from ..models import CostsModel
#
# logger = logging.getLogger(__name__)
#
#
# class CostsView(LoginRequiredMixin, View):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.table = CostsModel.objects.all()
#
#     def get(self, request, cost_id=None):
#         if not request.user.is_staff:
#             return HttpResponseForbidden()
#         if cost_id is not None:
#             c = get_object_or_404(CostsModel, pk=cost_id)
#         else:
#             c = None
#         form = CostsForm(instance=c)
#
#         return render(request, 'payment/costs.html', {'form': form, 'cost_id': cost_id, 'table': self.table})
#
#     def post(self, request, cost_id=None):
#         if cost_id is not None:
#             c = get_object_or_404(CostsModel, pk=cost_id)
#         else:
#             c = None
#         form = CostsForm(request.POST, instance=c)
#         if form.is_valid():
#             form.save()
#             form = CostsForm()
#             message = "Saved"
#         else:
#             logging.debug(form.errors)
#             message = 'Errors on form'
#         return render(request, 'payment/costs.html',
#                       {'form': form, 'table': self.table, 'cost_id': cost_id, 'message': message})
