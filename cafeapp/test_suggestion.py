from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cafe, CafeSuggestion


class SuggestionCompleteTests(TestCase):
    valid_data = {
        'name': '테스트 말차집',
        'city': 'seoul',
        'area': '성수',
        'address': '서울 성동구 어딘가 1',
        'menu_name': '말차 라떼',
        'price': 6500,
        'description': '테스트용 제보입니다.',
    }

    def test_submit_redirects_and_shows_suggested_cafe_name_once(self):
        response = self.client.post(reverse('cafe_suggestion'), self.valid_data, follow=True)

        self.assertRedirects(response, reverse('cafe_suggestion_complete'))
        self.assertContains(response, '테스트 말차집')
        self.assertEqual(CafeSuggestion.objects.filter(status='pending').count(), 1)

        # 새로고침하면 이름 없이 일반 문구만 보인다.
        again = self.client.get(reverse('cafe_suggestion_complete'))
        self.assertNotContains(again, '테스트 말차집')
        self.assertContains(again, '카페 제보가 접수되었어요.')

    def test_complete_page_without_submission_shows_generic_message(self):
        response = self.client.get(reverse('cafe_suggestion_complete'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '제보해 주셔서 고마워요')
        self.assertContains(response, reverse('cafe_suggestion'))
        self.assertContains(response, reverse('cafe_list'))

    def test_invalid_submission_does_not_remember_a_name(self):
        data = {**self.valid_data, 'price': ''}
        response = self.client.post(reverse('cafe_suggestion'), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CafeSuggestion.objects.count(), 0)
        self.assertNotContains(self.client.get(reverse('cafe_suggestion_complete')), '테스트 말차집')

    def test_name_is_escaped(self):
        data = {**self.valid_data, 'name': '<script>alert(1)</script>'}
        response = self.client.post(reverse('cafe_suggestion'), data, follow=True)

        self.assertNotContains(response, '<script>alert(1)</script>')


class SuggestionCityTests(TestCase):
    data = {
        'name': '시부야 말차집',
        'city': 'tokyo',
        'area': '시부야',
        'address': '2-1-1 Shibuya, Tokyo',
        'menu_name': '말차 라떼',
        'price': 700,
        'description': '도쿄 카페 제보입니다.',
    }

    def test_form_lists_cities_grouped_by_country(self):
        response = self.client.get(reverse('cafe_suggestion'))

        self.assertContains(response, '<optgroup label="한국">')
        self.assertContains(response, '<optgroup label="일본">')
        self.assertContains(response, '<option value="tokyo">도쿄</option>')
        self.assertContains(response, '<option value="seoul" selected>서울</option>')

    def test_country_is_derived_from_the_chosen_city(self):
        self.client.post(reverse('cafe_suggestion'), self.data)

        suggestion = CafeSuggestion.objects.get()
        self.assertEqual((suggestion.country, suggestion.city), ('JP', 'tokyo'))

    def test_unknown_or_missing_city_is_rejected(self):
        for city in ('atlantis', ''):
            response = self.client.post(reverse('cafe_suggestion'), {**self.data, 'city': city})
            self.assertEqual(response.status_code, 200)
        self.assertEqual(CafeSuggestion.objects.count(), 0)

    def test_posted_country_cannot_override_the_city(self):
        self.client.post(reverse('cafe_suggestion'), {**self.data, 'country': 'US'})

        self.assertEqual(CafeSuggestion.objects.get().country, 'JP')

    def test_existing_style_suggestions_default_to_seoul(self):
        suggestion = CafeSuggestion.objects.create(
            name='옛 제보', area='성수', address='서울', menu_name='라떼', price=1, description='d',
        )

        self.assertEqual((suggestion.country, suggestion.city), ('KR', 'seoul'))


class SuggestionApprovalTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser('admin', 'a@example.com', 'pw-for-tests')
        self.client.force_login(admin)

    def approve(self, suggestion):
        return self.client.post(reverse('admin:cafeapp_cafesuggestion_changelist'), {
            'action': 'approve_and_create_cafes',
            '_selected_action': [suggestion.pk],
        })

    def test_approving_creates_cafe_in_the_suggested_city(self):
        suggestion = CafeSuggestion.objects.create(
            country='JP', city='tokyo', name='시부야 말차집', area='시부야',
            address='Shibuya', menu_name='말차 라떼', price=700, description='d',
        )

        self.approve(suggestion)

        cafe = Cafe.objects.get(name='시부야 말차집')
        self.assertEqual((cafe.country, cafe.city), ('JP', 'tokyo'))
        suggestion.refresh_from_db()
        self.assertEqual(suggestion.status, CafeSuggestion.Status.APPROVED)

    def test_approving_twice_does_not_duplicate(self):
        suggestion = CafeSuggestion.objects.create(
            country='KR', city='jeju', name='제주 말차집', area='애월',
            address='Jeju', menu_name='말차 라떼', price=0, description='d',
        )

        self.approve(suggestion)
        self.approve(suggestion)

        self.assertEqual(Cafe.objects.filter(name='제주 말차집').count(), 1)

    def test_same_name_in_another_city_is_a_different_cafe(self):
        Cafe.objects.create(name='같은이름', country='KR', city='seoul', area='성수', address='a', menu_name='m', price=1, description='d')
        suggestion = CafeSuggestion.objects.create(
            country='JP', city='tokyo', name='같은이름', area='성수',
            address='a', menu_name='m', price=1, description='d',
        )

        self.approve(suggestion)

        self.assertEqual(Cafe.objects.filter(name='같은이름').count(), 2)
