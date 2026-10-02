import gettext
import importlib.util
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


def _load_script(name):
    path = Path(settings.BASE_DIR) / 'scripts' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnglishHomeTests(TestCase):
    def english(self, url):
        self.client.cookies['django_language'] = 'en'
        return self.client.get(url)

    def test_home_is_translated_in_english(self):
        response = self.english(reverse('cafe_list'))

        self.assertContains(response, 'Where shall we enjoy')
        self.assertContains(response, 'Seoul Map')
        self.assertContains(response, 'Matcha Guide')
        self.assertContains(response, 'Matcha Strength')
        self.assertContains(response, "Today's Matcha Fairy Picks")
        self.assertNotContains(response, '서울 지도')
        self.assertEqual(response.context['city_name'], 'Seoul')

    def test_area_chip_label_is_translated_but_filter_value_stays_korean(self):
        response = self.english(reverse('cafe_list'))

        self.assertContains(response, 'value="삼성"')
        self.assertContains(response, '>Samseong</button>')

    def test_home_stays_korean_by_default(self):
        response = self.client.get(reverse('cafe_list'))

        self.assertContains(response, '서울 지도')
        self.assertContains(response, '말차 가이드')
        self.assertNotContains(response, 'Seoul Map')
        self.assertEqual(response.context['city_name'], '서울')

    def test_map_popup_strings_are_passed_to_javascript_in_english(self):
        response = self.english(reverse('cafe_list'))

        self.assertContains(response, "photoPending: 'Photo coming soon'")
        self.assertContains(response, "reviews: '__N__ reviews'")


class TranslationCatalogTests(TestCase):
    def test_every_template_string_has_an_english_translation(self):
        check = _load_script('i18n_check')
        templates, po = check.template_msgids(), check.po_entries()

        missing = [msgid for msgid in templates if not po.get(msgid)]
        self.assertEqual(missing, [], '번역이 없는 문구가 있습니다. python scripts/i18n_check.py 로 확인하세요.')

    def test_compiled_mo_matches_po(self):
        compile_messages = _load_script('compile_messages')
        locale_dir = Path(settings.BASE_DIR) / 'locale' / 'en' / 'LC_MESSAGES'
        expected = compile_messages.parse_po(locale_dir / 'django.po')
        with open(locale_dir / 'django.mo', 'rb') as mo_file:
            compiled = gettext.GNUTranslations(mo_file)._catalog

        for msgid, msgstr in expected.items():
            if not msgid or '\0' in msgid:
                continue
            self.assertEqual(compiled.get(msgid), msgstr, f'.mo가 오래됨: {msgid}')
