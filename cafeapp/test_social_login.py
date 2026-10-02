from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse


class SocialLoginButtonTests(TestCase):
    def test_login_page_shows_coming_soon_when_no_app_is_configured(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '구글로 로그인 · 준비 중')
        self.assertContains(response, '카카오로 로그인 · 준비 중')
        self.assertNotContains(response, reverse('google_login'))
        self.assertNotContains(response, reverse('kakao_login'))

    def test_configured_provider_gets_a_working_link(self):
        app = SocialApp.objects.create(
            provider='google', name='google', client_id='test-id', secret='test-secret',
        )
        app.sites.add(Site.objects.get_current())

        response = self.client.get(reverse('login'))

        self.assertContains(response, f'href="{reverse("google_login")}"')
        self.assertNotContains(response, '구글로 로그인 · 준비 중')
        self.assertContains(response, '카카오로 로그인 · 준비 중')

    def test_password_login_form_is_still_there(self):
        response = self.client.get(reverse('login'))

        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
