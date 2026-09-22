from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .guide_content import GUIDE_ARTICLES, GUIDE_REGIONS, GUIDE_TASTES
from .models import Cafe


class GuideMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.ids, self.images = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs)
        if tag == 'img':
            self.images.append(attrs)


class MatchaGuideTests(TestCase):
    def test_public_guide_renders_sections_and_no_map_script(self):
        response = self.client.get(reverse('matcha_guide'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cafeapp/matcha_guide.html')
        for text in ['말차 가이드', '이런 글부터 읽어보세요', '내 취향 찾기', '지역별 말차 이야기', '카페 목록 보러가기']:
            self.assertContains(response, text)
        self.assertNotContains(response, 'L.map(')
        self.assertNotContains(response, '<script')
        self.assertEqual(len(response.context['guide_articles']), 4)
        self.assertEqual(len(response.context['guide_tastes']), 5)
        self.assertEqual(len(response.context['guide_regions']), 5)

    def test_only_current_navigation_is_active_on_each_shared_page(self):
        for route in ('cafe_list', 'cafe_catalog', 'matcha_guide'):
            response = self.client.get(reverse(route))
            markup = GuideMarkup(response.content.decode())
            active = [link for link in markup.links if link.get('aria-current') == 'page']
            self.assertEqual(len(active), 1)
            self.assertEqual(active[0]['href'].split('?')[0], reverse(route))
            self.assertContains(response, reverse('matcha_guide'))

    def test_anchors_and_images_exist(self):
        response = self.client.get(reverse('matcha_guide'))
        markup = GuideMarkup(response.content.decode())
        self.assertEqual(len(markup.ids), len(set(markup.ids)))
        for link in markup.links:
            if link.get('href', '').startswith('#'):
                self.assertIn(link['href'][1:], markup.ids)
            if link.get('target') == '_blank':
                self.assertEqual(link['rel'], 'noopener noreferrer')
        for item in GUIDE_ARTICLES + GUIDE_REGIONS:
            self.assertTrue(finders.find(item['image']), item['image'])
        self.assertTrue(finders.find('cafeapp/guide.css'))

    def test_preserves_search_favorites_recommendations_and_auth_links(self):
        response = self.client.get(reverse('matcha_guide'))
        for route in ('cafe_recommendations', 'cafe_catalog', 'favorite_list', 'login', 'signup', 'cafe_suggestion'):
            self.assertContains(response, reverse(route))
        self.assertContains(response, '/cafes/#search-input')
        self.assertContains(response, 'name="next" value="/guide/"')
        user = get_user_model().objects.create_user(username='guide-reader', password='test-password')
        self.client.force_login(user)
        response = self.client.get(reverse('matcha_guide'))
        self.assertContains(response, 'guide-reader')
        self.assertContains(response, reverse('logout'))

    def test_information_page_does_not_write_cafes(self):
        cafe = Cafe.objects.create(name='Keep cafe', area='성수', address='Test', menu_name='Matcha', price=6000, description='Keep')
        before = list(Cafe.objects.values())
        self.client.get(reverse('matcha_guide'), {'pick': '1'})
        self.assertEqual(before, list(Cafe.objects.values()))
        self.assertTrue(Cafe.objects.filter(pk=cafe.pk).exists())
        self.assertEqual([taste['name'] for taste in GUIDE_TASTES], ['말차 진하기', '쌉싸름함', '단맛', '우유맛', '말차 향'])
