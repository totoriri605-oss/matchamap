from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cafe, Favorite


class CafeCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        common = dict(menu_name='Matcha Latte', price=6000, description='진한 말차', address='Test')
        cls.seoul = [Cafe.objects.create(name=f'Seoul {i}', area='성수', **common) for i in range(4)]
        cls.ny = Cafe.objects.create(name='NY tea', area='NoHo', country='US', city='new-york',
                                     is_matchayojung_pick=True, matcha_strength=5, is_vegan=True, **common)
        cls.user = get_user_model().objects.create_user(username='catalog-reader', password='test-password')

    def test_catalog_renders_all_cards_without_home_map(self):
        response = self.client.get(reverse('cafe_catalog'))
        self.assertTemplateUsed(response, 'cafeapp/cafe_catalog.html')
        self.assertContains(response, '총 4개의 말차 카페')
        for cafe in self.seoul:
            self.assertContains(response, f'id="cafe-{cafe.pk}"')
            self.assertContains(response, reverse('cafe_detail', args=[cafe.pk]))
        self.assertNotContains(response, 'L.map(')
        self.assertContains(response, 'catalog.css')

    def test_shared_filters_and_city_links(self):
        params = dict(country='US', city='new-york', q='tea', pick='1', matcha_strength='4', is_vegan='on')
        catalog = self.client.get(reverse('cafe_catalog'), params)
        home = self.client.get(reverse('cafe_list'), params)
        self.assertEqual(list(catalog.context['cafes']), [self.ny])
        self.assertEqual(list(catalog.context['cafes']), list(home.context['cafes']))
        self.assertIn('pick=1', catalog.context['city_grid_choices'][0]['url'])
        self.assertContains(catalog, '말차요정 PICK')

    def test_empty_results_reset_keeps_city(self):
        response = self.client.get(reverse('cafe_catalog'), {'country': 'US', 'city': 'new-york', 'q': 'missing'})
        self.assertContains(response, '총 0개의 말차 카페')
        self.assertContains(response, '/cafes/?country=US&amp;city=new-york')

    def test_favorite_returns_to_filtered_catalog(self):
        self.client.force_login(self.user)
        target = f'/cafes/?country=US&city=new-york#cafe-{self.ny.pk}'
        response = self.client.post(reverse('toggle_favorite', args=[self.ny.pk]), {'next': target})
        self.assertRedirects(response, target)
        self.assertTrue(Favorite.objects.filter(user=self.user, cafe=self.ny).exists())

    def test_invalid_taste_shows_error_without_crashing(self):
        response = self.client.get(reverse('cafe_catalog'), {'matcha_strength': '99'})
        self.assertContains(response, '필터 값을 다시 확인해주세요.')
