from django.conf.urls import patterns, url, include
from django import forms

from zodb_light.contrib.form_data.views import FormDataCreateView


class ArtistForm(forms.Form):
    name = forms.CharField()


urlpatterns = patterns('',
    url(r'artists/create/$',
        FormDataCreateView.as_view(form_class=ArtistForm),
        name='artists_create'),
    url(r'formdata/', include('zodb_light.contrib.form_data.urls')),
)
