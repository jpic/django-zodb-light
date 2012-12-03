from django.test import TestCase
from django.conf import settings
from django.test.client import Client

from zodb_light.contrib.form_data.models import FormData

TEST_APP = 'zodb_light.contrib.form_data.tests.test_app'


class ViewTestCase(TestCase):
    urls = TEST_APP + '.urls'

    def setUp(self):
        self.client = Client()
        if TEST_APP not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS += (TEST_APP,)

    def test_create(self):
        response = self.client.get('/artists/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('id_name' in response.content)

        response = self.client.post('/artists/create/', {'name': 'bbq bob'})

        self.assertEqual(1, len(FormData.db))
        self.assertEqual(response.status_code, 302)

        for uuid, model in FormData.db.items():
            pass

        self.assertEqual(response['Location'],
            'http://testserver/formdata/' + str(uuid) + '/')

        response = self.client.get(response['Location'])
        self.assertTrue('name' in response.content)
        self.assertTrue('bbq bob' in response.content)
