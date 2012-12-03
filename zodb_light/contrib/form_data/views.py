from django.views import generic
from django import http

from models import FormData


class FormDataCreateView(generic.FormView):
    template_name = 'zodb_light/contrib/form_data/form_data_form.html'

    def get_success_url(self):
        return self.form_data.get_absolute_url()

    def form_valid(self, form):
        self.form_data = FormData(self.form_class, form.cleaned_data)
        return http.HttpResponseRedirect(self.get_success_url())


class FormDataDetailView(generic.TemplateView):
    template_name = 'zodb_light/contrib/form_data/form_data_detail.html'

    def get_context_data(self, **kwargs):
        context = super(FormDataDetailView, self).get_context_data(**kwargs)
        context['form_data'] = FormData.get(kwargs['uuid'])
        return context
