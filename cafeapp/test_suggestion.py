from django.test import TestCase
from django.urls import reverse

from .models import CafeSuggestion


class SuggestionCompleteTests(TestCase):
    valid_data = {
        'name': '테스트 말차집',
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
