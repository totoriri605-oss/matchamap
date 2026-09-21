from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Cafe


class CityNavigationTests(TestCase):
    def setUp(self):
        common = dict(menu_name='Matcha', price=6000, description='Tea', address='Test')
        self.seoul = Cafe.objects.create(name='Seoul tea', area='성수', **common)
        self.ny = Cafe.objects.create(name='NY tea', area='NoHo', country='US', city='new-york', latitude=40.726, longitude=-73.992, is_matchayojung_pick=True, matcha_strength=5, **common)

    def test_city_isolates_cards_and_map_and_combines_filters(self):
        response = self.client.get(reverse('cafe_list'), {'country': 'US', 'city': 'new-york', 'pick': '1', 'q': 'tea', 'matcha_strength': '4'})
        self.assertEqual(list(response.context['cafes']), [self.ny])
        self.assertEqual([c['name'] for c in response.context['map_cafes']], ['NY tea'])
        self.assertTrue(response.context['map_cafes'][0]['is_pick'])
        self.assertContains(response, 'name="city" value="new-york"')
        self.assertIn('pick=1', response.context['city_grid_choices'][0]['url'])

    def test_default_and_invalid_selection_fall_back_to_seoul(self):
        for params in ({}, {'country': 'invalid', 'city': 'tokyo'}):
            response = self.client.get(reverse('cafe_list'), params)
            self.assertEqual(list(response.context['cafes']), [self.seoul])

    def test_empty_city_keeps_city_bounds(self):
        response = self.client.get(reverse('cafe_list'), {'country': 'JP', 'city': 'osaka', 'area': '성수'})
        self.assertEqual(response.context['result_count'], 0)
        self.assertEqual(response.context['city_name'], '오사카')
        self.assertIsNone(response.context['selected_area'])
        self.assertEqual(response.context['map_cafes'], [])
        self.assertTrue(response.context['city_bounds'])

    def test_admin_model_validation_rejects_mismatched_country(self):
        self.ny.country = 'JP'
        with self.assertRaises(ValidationError):
            self.ny.full_clean()
