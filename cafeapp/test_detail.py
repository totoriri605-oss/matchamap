from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cafe, Favorite, Review


class CafeDetailPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('reader', password='pw-for-tests')
        cls.full = Cafe.objects.create(
            name='풀 카페', country='KR', city='seoul', area='성수', address='서울 성동구 아차산로 1',
            menu_name='말차 라떼', price=6500, description='설명 문장입니다.', business_hours='10:00~20:00',
            matcha_strength=4, bitterness=3, sweetness=2, matcha_aroma=5,
            is_decaf=True, has_takeout=True, is_matchayojung_pick=True,
            matchayojung_comment='진해요', blog_url='https://example.com/review',
            latitude='37.54', longitude='127.05',
        )
        cls.bare = Cafe.objects.create(
            name='빈 카페', country='JP', city='tokyo', area='시부야', address='1-2-3 Shibuya, Tokyo',
            menu_name='말차', price=0, description='정보가 거의 없습니다.',
        )

    def get(self, cafe, **extra):
        return self.client.get(reverse('cafe_detail', args=[cafe.id]), **extra)

    def test_page_uses_the_shared_site_header_with_catalog_tab_active(self):
        response = self.get(self.full)

        self.assertContains(response, 'site-nav')
        self.assertContains(response, 'site-brand__rabbit')
        self.assertContains(response, 'lang-switch')
        self.assertContains(response, 'aria-current="page">카페 목록</a>')

    def test_core_information_is_still_shown(self):
        response = self.get(self.full)

        for text in ('풀 카페', '서울 성동구 아차산로 1', '말차 라떼', '설명 문장입니다.', '10:00~20:00',
                     '서울 · 성수', '말차요정 PICK', '진해요', 'https://example.com/review'):
            self.assertContains(response, text)

    def test_price_has_thousands_separator_and_unknown_price_is_explained(self):
        self.assertContains(self.get(self.full), '6,500원')
        self.assertNotContains(self.get(self.full), '6500원')
        self.assertContains(self.get(self.bare), '가격 정보 확인 중')

    def test_business_hours_row_is_hidden_when_empty(self):
        self.assertContains(self.get(self.full), '영업시간')
        self.assertNotContains(self.get(self.bare), '영업시간')

    def test_set_taste_values_are_drawn_as_leaves_and_unset_ones_are_listed(self):
        response = self.get(self.full)

        self.assertEqual([row['label'] for row in response.context['taste_rows']], ['진하기', '쌉싸름함', '단맛', '말차 향'])
        self.assertContains(response, 'aria-label="진하기 4/5"')
        self.assertContains(response, 'aria-label="말차 향 5/5"')
        self.assertContains(response, '아직 등록되지 않은 맛 정보: 우유맛')
        self.assertContains(response, 'class="leaf is-on"', count=4 + 3 + 2 + 5)

    def test_cafe_without_taste_scores_shows_the_coming_soon_message(self):
        response = self.get(self.bare)

        self.assertContains(response, '맛 정보 준비 중입니다.')
        self.assertNotContains(response, 'taste-bars')

    def test_directions_links_depend_on_the_country(self):
        korean = self.get(self.full)
        self.assertContains(korean, '구글 지도')
        self.assertContains(korean, '네이버 지도')
        self.assertContains(korean, 'https://map.naver.com/p/search/')
        self.assertContains(korean, 'https://www.google.com/maps/search/?api=1&amp;query=')

        japanese = self.get(self.bare)
        self.assertContains(japanese, '구글 지도')
        self.assertNotContains(japanese, '네이버 지도')

    def test_directions_query_is_url_encoded(self):
        google = self.get(self.full).context['directions'][0]['url']

        self.assertIn('%ED%92%80%20%EC%B9%B4%ED%8E%98', google)  # '풀 카페'
        self.assertNotIn(' ', google)

    def test_external_links_open_safely(self):
        response = self.get(self.full)

        self.assertContains(response, 'target="_blank" rel="noopener noreferrer">구글 지도')

    def test_map_button_only_appears_for_cafes_with_coordinates(self):
        self.assertContains(self.get(self.full), '지도에서 보기')
        self.assertNotContains(self.get(self.bare), '지도에서 보기')

    def test_back_link_goes_to_the_catalog_of_the_same_city(self):
        response = self.get(self.bare)

        self.assertContains(response, '/cafes/?country=JP&amp;city=tokyo')

    def test_placeholder_is_shown_without_a_photo(self):
        response = self.get(self.bare)

        self.assertContains(response, 'detail-photo__empty')
        self.assertContains(response, '사진 준비 중')

    def test_favorite_button_state(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.get(self.full), 'detail-btn--primary is-on')
        self.assertContains(self.get(self.full), '♡ 가보고 싶어요')

        Favorite.objects.create(user=self.user, cafe=self.full)
        self.assertContains(self.get(self.full), 'detail-btn--primary is-on')
        self.assertContains(self.get(self.full), '♥ 가보고 싶어요')

    def test_reviews_and_summary_are_displayed(self):
        Review.objects.create(cafe=self.full, author=self.user, rating=5, comment='최고예요')

        response = self.get(self.full)

        self.assertContains(response, '평균 5.0점')
        self.assertContains(response, '리뷰 1개')
        self.assertContains(response, '최고예요')

    def test_invalid_review_redisplays_the_new_layout_with_400(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('review_create', args=[self.full.id]), {'rating': 5, 'comment': ''})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '한줄평을 입력해주세요.', status_code=400)
        self.assertContains(response, 'site-nav', status_code=400)
        self.assertContains(response, 'aria-label="진하기 4/5"', status_code=400)
        self.assertContains(response, '6,500원', status_code=400)

    def test_english_labels(self):
        self.client.cookies['django_language'] = 'en'

        response = self.get(self.full)

        for text in ('Back to cafes', 'Directions', 'Google Maps', 'Naver Map', 'Seoul · Seongsu', 'Not yet rated: Milkiness', '₩6,500'):
            self.assertContains(response, text)
        self.assertNotContains(response, '길찾기')
