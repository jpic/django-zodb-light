from django.conf.urls import patterns, url

import views

UUID_REGEXP = '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'

urlpatterns = patterns('',
    url(r'(?P<uuid>'+UUID_REGEXP+')/$',
        views.FormDataDetailView.as_view(),
        name='form_data_form_data_detail'),
)
