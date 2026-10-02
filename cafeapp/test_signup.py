from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignupTests(TestCase):
    data = {'username': 'newbie', 'password1': 'Str0ng-pass-123', 'password2': 'Str0ng-pass-123'}

    def test_signup_creates_account_and_logs_in(self):
        response = self.client.post(reverse('signup'), self.data, follow=True)

        self.assertRedirects(response, reverse('cafe_list'))
        self.assertTrue(get_user_model().objects.filter(username='newbie').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), get_user_model().objects.get().pk)

    def test_signup_with_mismatched_passwords_shows_form_again(self):
        response = self.client.post(reverse('signup'), {**self.data, 'password2': 'different'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.exists())

    def test_logged_in_user_is_redirected_away_from_signup(self):
        self.client.post(reverse('signup'), self.data)

        self.assertRedirects(self.client.get(reverse('signup')), reverse('cafe_list'))
