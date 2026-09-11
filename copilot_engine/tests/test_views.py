import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'sectors_copilot.settings'

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_contains_title(self):
        response = self.client.get('/')
        self.assertContains(response, '<title>')

    def test_homepage_loads_tailwind(self):
        response = self.client.get('/')
        self.assertContains(response, 'app.css')

    def test_homepage_loads_tailwind_class(self):
        response = self.client.get('/')
        content = response.content.decode()
        # Tailwind base classes should be in compiled CSS
        self.assertIn('bg-surface', content) or self.assertIn('flex', content)