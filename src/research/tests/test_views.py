import os

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

import django
django.setup()

from django.test import Client, TestCase


class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_contains_title(self):
        response = self.client.get("/")
        self.assertContains(response, "<title>")

    def test_homepage_loads_tailwind(self):
        response = self.client.get("/")
        self.assertContains(response, "app.css")

    def test_homepage_loads_tailwind_class(self):
        response = self.client.get("/")
        content = response.content.decode()
        self.assertTrue("bg-surface" in content or "flex" in content)
