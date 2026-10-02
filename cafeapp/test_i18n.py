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


class EnglishScreensTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        from .models import Cafe, Favorite

        cls.cafe = Cafe.objects.create(
            name='Test cafe', country='KR', city='seoul', area='성수', address='addr',
            menu_name='Latte', price=6500, description='d', business_hours='10:00',
            matcha_strength=4, bitterness=3, sweetness=2, milkiness=3, matcha_aroma=4,
        )
        cls.user = get_user_model().objects.create_user('reader', password='pw-for-tests')
        Favorite.objects.create(user=cls.user, cafe=cls.cafe)

    def english(self, url, **params):
        self.client.cookies['django_language'] = 'en'
        return self.client.get(url, params)

    def test_catalog_is_translated(self):
        response = self.english(reverse('cafe_catalog'))

        for text in ('Reset filters', 'Choose a city', 'Matcha strength · min', 'Your next cup of matcha',
                     'Recommended · coming soon', '1 matcha cafe in total', 'All of Seoul', '>Seoul</a>', '>Tokyo</a>'):
            self.assertContains(response, text)
        self.assertNotContains(response, '조건 초기화')
        self.assertContains(response, 'value="성수"')  # 필터 값은 한국어 그대로

    def test_catalog_empty_state_and_active_filters_are_translated(self):
        response = self.english(reverse('cafe_catalog'), q='nothing-matches', area='성수')

        self.assertContains(response, 'Search: nothing-matches')
        self.assertContains(response, "We couldn't find a cafe in Seoul that matches your filters.")
        self.assertContains(response, 'Area: Seongsu')

    def test_detail_page_is_translated(self):
        response = self.english(reverse('cafe_detail', args=[self.cafe.id]))

        for text in ('Hours', 'Address', 'Matcha taste profile', 'Strength', 'Milkiness', 'Add to favorites',
                     'No reviews yet. Be the first to leave one!', '>Log in</a> to leave a one-line review.'):
            self.assertContains(response, text)
        self.assertNotContains(response, '영업시간')

    def test_recommendations_page_is_translated(self):
        response = self.english(reverse('cafe_recommendations'))

        self.assertContains(response, 'Find my matcha cafe')
        self.assertContains(response, 'Preferred strength')
        self.assertContains(response, 'Decaf required')

    def test_recommendation_result_is_translated(self):
        response = self.english(reverse('cafe_recommendations'), matcha_strength=4, bitterness=3, sweetness=2,
                                milkiness=3, matcha_aroma=4)

        self.assertContains(response, '100% match')
        self.assertContains(response, '#1')
        self.assertContains(response, 'most closely')

    def test_favorites_page_and_messages_are_translated(self):
        self.client.login(username='reader', password='pw-for-tests')
        favorites = self.english(reverse('favorite_list'))
        self.assertContains(favorites, '1 saved cafe')
        self.assertContains(favorites, 'Remove from favorites')

        posted = self.client.post(reverse('review_create', args=[self.cafe.id]), {'rating': 5, 'comment': 'nice'}, follow=True)
        self.assertContains(posted, 'Your review has been posted.')

    def test_korean_remains_the_default_for_translated_screens(self):
        response = self.client.get(reverse('cafe_catalog'))

        self.assertContains(response, '조건 초기화')
        self.assertContains(response, '총 1개의 말차 카페')
        self.assertNotContains(response, 'Reset filters')
