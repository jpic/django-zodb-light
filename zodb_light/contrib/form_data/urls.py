from django.conf.urls import patterns, url

import zodb_light

import views

urlpatterns = patterns('',
    url(r'(?P<uuid>'+zodb_light.UUID_REGEXP+')/$',
        views.FormDataDetailView.as_view(),
        name='form_data_form_data_detail'),
    url(r'(?P<uuid>'+zodb_light.UUID_REGEXP+')/update/$',
        views.FormDataUpdateView.as_view(),
        name='form_data_form_data_update'),
)
