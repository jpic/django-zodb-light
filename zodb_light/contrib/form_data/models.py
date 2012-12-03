from django.core.urlresolvers import reverse

from zodb_light.models import Model


class FormData(Model):
    def __init__(self, form_class, form_cleaned_data):
        self.form_class = form_class
        self.form_data = form_cleaned_data
        super(FormData, self).__init__(form_cleaned_data['name'])

    def get_absolute_url(self):
        return reverse('form_data_form_data_detail', args=(
            str(self.__objectid__),))
