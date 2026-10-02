import os
import re
import tempfile
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from .templatetags.static_version import static_v


class StaticVersionTests(TestCase):
    def test_url_gets_a_version_from_the_file_modification_time(self):
        url = static_v('cafeapp/home.css')

        self.assertRegex(url, r'^/static/cafeapp/home\.css\?v=\d+$')

    def test_version_changes_when_the_file_changes(self):
        with tempfile.NamedTemporaryFile(suffix='.css', delete=False) as handle:
            path = handle.name
        try:
            os.utime(path, (1_000_000_000, 1_000_000_000))
            with mock.patch('cafeapp.templatetags.static_version.finders.find', return_value=path):
                first = static_v('cafeapp/x.css')
                os.utime(path, (1_000_000_500, 1_000_000_500))
                second = static_v('cafeapp/x.css')
        finally:
            os.unlink(path)

        self.assertTrue(first.endswith('?v=1000000000'))
        self.assertTrue(second.endswith('?v=1000000500'))

    def test_missing_file_falls_back_to_the_plain_url(self):
        self.assertEqual(static_v('cafeapp/does-not-exist.css'), '/static/cafeapp/does-not-exist.css')

    def test_pages_link_versioned_stylesheets(self):
        expected = {
            reverse('cafe_list'): 'home.css',
            reverse('cafe_catalog'): 'catalog.css',
            reverse('matcha_guide'): 'guide.css',
            reverse('cafe_suggestion'): 'suggestion.css',
            reverse('cafe_suggestion_complete'): 'suggestion.css',
        }
        for url, css in expected.items():
            html = self.client.get(url).content.decode()
            self.assertRegex(html, rf'/static/cafeapp/{re.escape(css)}\?v=\d+', url)
