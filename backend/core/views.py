from django.shortcuts import render
from core.mixins import AuthMixin
from django.views.generic import TemplateView
from core.dashboard_service import get_dashboard_data


class DashboardView(AuthMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_dashboard_data(self.request.user))
        return ctx