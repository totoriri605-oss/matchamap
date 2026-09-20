from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .forms import CafeTasteFilterForm
from .models import Cafe, Favorite, Review


class ReviewFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cafe = Cafe.objects.create(
            name='테스트 말차 카페',
            area='성수',
            address='서울시 성동구',
            menu_name='말차 라테',
            price=6500,
            description='진한 말차 카페',
        )
        cls.user = get_user_model().objects.create_user(
            username='matcha_lover',
            password='safe-password-123',
        )
        cls.other_user = get_user_model().objects.create_user(
            username='other_user',
            password='safe-password-123',
        )

    def test_rating_must_be_between_one_and_five(self):
        review = Review(
            cafe=self.cafe,
            author=self.user,
            rating=6,
            comment='맛있어요',
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_user_can_write_only_one_review_per_cafe(self):
        Review.objects.create(
            cafe=self.cafe,
            author=self.user,
            rating=5,
            comment='첫 리뷰',
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(
                cafe=self.cafe,
                author=self.user,
                rating=4,
                comment='중복 리뷰',
            )

    def test_logged_in_user_can_create_review(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('review_create', args=[self.cafe.id]),
            {'rating': 5, 'comment': '진하고 맛있어요'},
        )
        self.assertRedirects(response, reverse('cafe_detail', args=[self.cafe.id]))
        self.assertTrue(
            Review.objects.filter(cafe=self.cafe, author=self.user, rating=5).exists()
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.post(
            reverse('review_create', args=[self.cafe.id]),
            {'rating': 5, 'comment': '맛있어요'},
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('review_create', args=[self.cafe.id])}",
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_invalid_review_shows_form_errors(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('review_create', args=[self.cafe.id]),
            {'rating': 5, 'comment': '   '},
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '한줄평을 입력해주세요.', status_code=400)

    def test_author_can_delete_own_review(self):
        review = Review.objects.create(
            cafe=self.cafe,
            author=self.user,
            rating=5,
            comment='삭제할 리뷰',
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('review_delete', args=[self.cafe.id, review.id])
        )
        self.assertRedirects(response, reverse('cafe_detail', args=[self.cafe.id]))
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_user_cannot_delete_another_users_review(self):
        review = Review.objects.create(
            cafe=self.cafe,
            author=self.user,
            rating=5,
            comment='다른 사용자의 리뷰',
        )
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('review_delete', args=[self.cafe.id, review.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_detail_page_displays_reviews_and_average(self):
        Review.objects.create(
            cafe=self.cafe,
            author=self.user,
            rating=5,
            comment='정말 진해요',
        )
        Review.objects.create(
            cafe=self.cafe,
            author=self.other_user,
            rating=3,
            comment='조금 달아요',
        )
        response = self.client.get(reverse('cafe_detail', args=[self.cafe.id]))
        self.assertContains(response, '평균 4.0점')
        self.assertContains(response, '리뷰 2개')
        self.assertContains(response, '정말 진해요')
        self.assertContains(response, '조금 달아요')

    def test_get_request_does_not_create_or_delete_review(self):
        review = Review.objects.create(
            cafe=self.cafe,
            author=self.user,
            rating=4,
            comment='유지될 리뷰',
        )
        self.client.force_login(self.user)
        self.client.get(reverse('review_create', args=[self.cafe.id]))
        self.client.get(reverse('review_delete', args=[self.cafe.id, review.id]))
        self.assertEqual(Review.objects.count(), 1)


class CafeTasteFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.strong_cafe = Cafe.objects.create(
            name='진한 말차 연구소',
            area='성수',
            address='서울시 성동구 1',
            latitude=37.544000,
            longitude=127.056000,
            menu_name='진한 말차',
            price=7000,
            description='진하고 덜 단 말차',
            matcha_strength=5,
            bitterness=4,
            sweetness=1,
            milkiness=1,
            matcha_aroma=5,
            is_vegan=True,
            has_takeout=True,
        )
        cls.sweet_cafe = Cafe.objects.create(
            name='달콤 말차 카페',
            area='삼성',
            address='서울시 강남구 2',
            latitude=37.510000,
            longitude=127.060000,
            menu_name='말차 라테',
            price=6500,
            description='부드럽고 달콤한 말차',
            matcha_strength=3,
            bitterness=2,
            sweetness=4,
            milkiness=4,
            matcha_aroma=3,
            is_decaf=True,
            has_parking=True,
        )
        cls.unknown_cafe = Cafe.objects.create(
            name='미등록 말차 카페',
            area='성수',
            address='서울시 성동구 3',
            menu_name='말차',
            price=6000,
            description='취향 정보 등록 전',
        )

    def cafe_names(self, response):
        return set(response.context['cafes'].values_list('name', flat=True))

    def test_taste_scores_allow_one_five_and_none(self):
        for value in (1, 5, None):
            with self.subTest(value=value):
                cafe = Cafe(
                    name='검증 카페',
                    area='성수',
                    address='서울',
                    menu_name='말차',
                    price=5000,
                    description='검증',
                    matcha_strength=value,
                )
                cafe.full_clean()

    def test_taste_scores_reject_values_outside_range(self):
        for value in (0, 6):
            with self.subTest(value=value):
                cafe = Cafe(
                    name='검증 카페',
                    area='성수',
                    address='서울',
                    menu_name='말차',
                    price=5000,
                    description='검증',
                    matcha_strength=value,
                )
                with self.assertRaises(ValidationError):
                    cafe.full_clean()

    def test_convenience_fields_default_to_false(self):
        cafe = Cafe()
        self.assertFalse(cafe.is_decaf)
        self.assertFalse(cafe.is_vegan)
        self.assertFalse(cafe.has_parking)
        self.assertFalse(cafe.has_takeout)

    def test_filter_form_validates_and_converts_values(self):
        form = CafeTasteFilterForm(
            {'matcha_strength': '4', 'sweetness': '2', 'is_vegan': 'on'}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['matcha_strength'], 4)
        self.assertEqual(form.cleaned_data['sweetness'], 2)
        self.assertTrue(form.cleaned_data['is_vegan'])
        self.assertIsNone(form.cleaned_data['bitterness'])

        for invalid_value in ('0', '6', 'not-a-number'):
            with self.subTest(invalid_value=invalid_value):
                invalid_form = CafeTasteFilterForm(
                    {'matcha_strength': invalid_value}
                )
                self.assertFalse(invalid_form.is_valid())

    def test_each_taste_filter_uses_the_expected_boundary(self):
        filters = (
            {'matcha_strength': 4},
            {'bitterness': 3},
            {'sweetness': 2},
            {'milkiness': 2},
            {'matcha_aroma': 4},
        )
        for params in filters:
            with self.subTest(params=params):
                response = self.client.get(reverse('cafe_list'), params)
                self.assertEqual(
                    self.cafe_names(response),
                    {self.strong_cafe.name},
                )

    def test_convenience_filters_can_be_combined(self):
        response = self.client.get(
            reverse('cafe_list'),
            {'is_vegan': 'on', 'has_takeout': 'on'},
        )
        self.assertEqual(self.cafe_names(response), {self.strong_cafe.name})

        response = self.client.get(
            reverse('cafe_list'),
            {'is_decaf': 'on', 'has_parking': 'on'},
        )
        self.assertEqual(self.cafe_names(response), {self.sweet_cafe.name})

    def test_area_search_and_taste_filters_work_together(self):
        response = self.client.get(
            reverse('cafe_list'),
            {
                'area': '성수',
                'q': '진한',
                'matcha_strength': 4,
                'sweetness': 2,
                'is_vegan': 'on',
                'has_takeout': 'on',
            },
        )
        self.assertEqual(self.cafe_names(response), {self.strong_cafe.name})
        self.assertEqual(response.context['result_count'], 1)
        self.assertEqual(
            {cafe['name'] for cafe in response.context['map_cafes']},
            {self.strong_cafe.name},
        )

    def test_unknown_taste_values_are_excluded_from_score_filters(self):
        response = self.client.get(
            reverse('cafe_list'),
            {'matcha_strength': 1},
        )
        self.assertNotIn(self.unknown_cafe.name, self.cafe_names(response))

    def test_invalid_filter_is_safe_and_displays_an_error(self):
        response = self.client.get(
            reverse('cafe_list'),
            {'matcha_strength': 6},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 3)
        self.assertContains(response, '필터 값을 다시 확인해주세요.')

    def test_filter_selection_and_card_information_are_displayed(self):
        response = self.client.get(
            reverse('cafe_list'),
            {'matcha_strength': 4, 'is_vegan': 'on'},
        )
        self.assertEqual(
            response.context['taste_filter_form']['matcha_strength'].value(),
            '4',
        )
        self.assertContains(response, '진하기 5')
        self.assertContains(response, '단맛 1')
        self.assertContains(response, '비건')
        self.assertNotContains(response, self.sweet_cafe.name)

    def test_unknown_card_and_detail_taste_information_are_displayed(self):
        list_response = self.client.get(reverse('cafe_list'))
        self.assertContains(list_response, '맛 정보 준비 중')

        detail_response = self.client.get(
            reverse('cafe_detail', args=[self.strong_cafe.id])
        )
        self.assertContains(detail_response, '말차 취향 정보')
        self.assertContains(detail_response, '쌉싸름함')
        self.assertContains(detail_response, '테이크아웃')


class CafeRecommendationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cafes = []
        for index, score in enumerate((5, 4, 3, 2), start=1):
            cls.cafes.append(
                Cafe.objects.create(
                    name=f'추천 카페 {index}',
                    area='성수',
                    address=f'서울시 성동구 {index}',
                    menu_name='말차 라테',
                    price=6000 + index * 100,
                    description='추천 테스트 카페',
                    matcha_strength=score,
                    bitterness=score,
                    sweetness=score,
                    milkiness=score,
                    matcha_aroma=score,
                    is_vegan=index == 1,
                    has_takeout=index <= 2,
                )
            )
        cls.incomplete_cafe = Cafe.objects.create(
            name='점수 미등록 카페',
            area='성수',
            address='서울시 성동구 99',
            menu_name='말차',
            price=5000,
            description='일부 점수 미등록',
            matcha_strength=5,
        )

    def preference_params(self, score=5, **extra):
        params = {
            'matcha_strength': score,
            'bitterness': score,
            'sweetness': score,
            'milkiness': score,
            'matcha_aroma': score,
        }
        params.update(extra)
        return params

    def test_page_initially_displays_only_the_preference_form(self):
        response = self.client.get(reverse('cafe_recommendations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '내 취향 말차 카페 찾기')
        self.assertEqual(response.context['recommendations'], [])
        self.assertNotContains(response, '취향과 가까운 말차 카페')

    def test_closest_three_cafes_are_ranked_by_total_difference(self):
        response = self.client.get(
            reverse('cafe_recommendations'),
            self.preference_params(5),
        )
        recommendations = response.context['recommendations']
        self.assertEqual(len(recommendations), 3)
        self.assertEqual(
            [result['cafe'].name for result in recommendations],
            ['추천 카페 1', '추천 카페 2', '추천 카페 3'],
        )
        self.assertEqual(recommendations[0]['match_percentage'], 100)
        self.assertEqual(recommendations[1]['match_percentage'], 75)

    def test_cafe_with_incomplete_taste_scores_is_excluded(self):
        response = self.client.get(
            reverse('cafe_recommendations'),
            self.preference_params(5),
        )
        names = [
            result['cafe'].name
            for result in response.context['recommendations']
        ]
        self.assertNotIn(self.incomplete_cafe.name, names)

    def test_required_convenience_options_filter_candidates(self):
        response = self.client.get(
            reverse('cafe_recommendations'),
            self.preference_params(5, is_vegan='on', has_takeout='on'),
        )
        recommendations = response.context['recommendations']
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['cafe'], self.cafes[0])

    def test_invalid_preferences_do_not_produce_recommendations(self):
        params = self.preference_params(5)
        params['sweetness'] = 6
        response = self.client.get(reverse('cafe_recommendations'), params)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.context['recommendations'], [])
        self.assertContains(
            response,
            '모든 맛 항목을 1점부터 5점 사이로 선택해주세요.',
        )

    def test_result_page_contains_reason_detail_and_favorite_actions(self):
        response = self.client.get(
            reverse('cafe_recommendations'),
            self.preference_params(5),
        )
        self.assertContains(response, '100% 일치')
        self.assertContains(response, '원하는 취향과 가장 비슷해요.')
        self.assertContains(
            response,
            reverse('cafe_detail', args=[self.cafes[0].id]),
        )
        self.assertContains(
            response,
            reverse('toggle_favorite', args=[self.cafes[0].id]),
        )


class FavoriteScrollPositionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cafe = Cafe.objects.create(
            name='스크롤 테스트 카페',
            area='성수',
            address='서울시 성동구',
            menu_name='말차 라테',
            price=6000,
            description='스크롤 위치 테스트',
            matcha_strength=5,
            bitterness=4,
            sweetness=2,
            milkiness=2,
            matcha_aroma=5,
        )
        cls.user = get_user_model().objects.create_user(
            username='favorite-tester',
            password='testpass123',
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_list_favorite_redirect_keeps_query_and_card_anchor(self):
        next_url = f'/?area=성수&matcha_strength=4#cafe-{self.cafe.id}'
        response = self.client.post(
            reverse('toggle_favorite', args=[self.cafe.id]),
            {'next': next_url},
        )
        self.assertEqual(response.status_code, 302)
        expected_url = (
            f'/?area={quote("성수")}&matcha_strength=4#cafe-{self.cafe.id}'
        )
        self.assertEqual(response.url, expected_url)

    def test_recommendation_favorite_redirect_keeps_card_anchor(self):
        next_url = (
            '/recommendations/?matcha_strength=5&bitterness=4&sweetness=2'
            f'&milkiness=2&matcha_aroma=5#recommendation-{self.cafe.id}'
        )
        response = self.client.post(
            reverse('toggle_favorite', args=[self.cafe.id]),
            {'next': next_url},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_favorite_list_removal_redirects_to_list_anchor(self):
        Favorite.objects.create(user=self.user, cafe=self.cafe)
        next_url = f"{reverse('favorite_list')}#favorite-list"
        response = self.client.post(
            reverse('toggle_favorite', args=[self.cafe.id]),
            {'next': next_url},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_list_template_targets_the_favorited_card(self):
        response = self.client.get(reverse('cafe_list'))
        self.assertContains(response, f'id="cafe-{self.cafe.id}"')
        self.assertContains(response, f'#cafe-{self.cafe.id}')

    def test_external_next_url_is_still_rejected(self):
        response = self.client.post(
            reverse('toggle_favorite', args=[self.cafe.id]),
            {'next': 'https://example.com/unsafe#cafe-1'},
        )
        self.assertEqual(
            response.url,
            reverse('cafe_detail', args=[self.cafe.id]),
        )


class CafeAdminImageTests(TestCase):
    def setUp(self):
        import tempfile
        from django.test import override_settings

        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        settings_override = override_settings(MEDIA_ROOT=self.media.name)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.admin_user = get_user_model().objects.create_superuser(
            username='photo_admin', password='test-password', email='admin@example.com',
        )
        self.cafe = Cafe.objects.create(
            name='사진 카페', area='성수', address='서울', menu_name='말차',
            price=6000, description='사진 테스트',
        )
        self.url = reverse('admin:cafeapp_cafe_change', args=[self.cafe.pk])
        self.data = {
            'name': self.cafe.name, 'area': '성수', 'address': '서울',
            'menu_name': '말차', 'price': 6000, 'description': '사진 테스트',
            '_save': '저장',
        }

    def photo(self, name):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        data = BytesIO()
        Image.new('RGB', (16, 16), 'green').save(data, format='PNG')
        return SimpleUploadedFile(name, data.getvalue(), content_type='image/png')

    def test_admin_upload_replace_and_clear_photo(self):
        self.client.force_login(self.admin_user)
        self.assertContains(self.client.get(self.url), '대표 사진')
        for name in ('first.png', 'replacement.png'):
            response = self.client.post(self.url, {**self.data, 'image': self.photo(name)})
            self.assertEqual(response.status_code, 302)
            self.cafe.refresh_from_db()
            self.assertTrue(self.cafe.image.name.endswith(name))
            self.assertTrue(self.cafe.image.storage.exists(self.cafe.image.name))
            self.assertContains(self.client.get(reverse('cafe_list')), self.cafe.image.url)
            self.assertContains(self.client.get(self.url), self.cafe.image.url)
        self.assertEqual(self.client.post(self.url, {**self.data, 'image-clear': 'on'}).status_code, 302)
        self.cafe.refresh_from_db()
        self.assertFalse(self.cafe.image)

    def test_photo_edit_link_and_admin_access_require_permission(self):
        self.assertNotContains(self.client.get(reverse('cafe_list')), '사진 편집')
        self.assertEqual(self.client.get(self.url).status_code, 302)
        staff = get_user_model().objects.create_user(username='no_photo_permission', is_staff=True)
        self.client.force_login(staff)
        self.assertNotContains(self.client.get(reverse('cafe_list')), '사진 편집')
        self.assertEqual(self.client.post(self.url, self.data).status_code, 403)
        self.client.force_login(self.admin_user)
        self.assertContains(self.client.get(reverse('cafe_list')), '사진 편집')


class HeroBannerTests(TestCase):
    setUp = CafeAdminImageTests.setUp
    photo = CafeAdminImageTests.photo

    def test_banner_lifecycle_and_fallback(self):
        from .models import HeroBanner

        self.assertContains(self.client.get(reverse('cafe_list')), 'class="matcha-art"')
        self.client.force_login(self.admin_user)
        add_url = reverse('admin:cafeapp_herobanner_add')
        response = self.client.post(add_url, {'image': self.photo('hero.png'), 'position': 'left', '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        banner = HeroBanner.objects.get()
        url = reverse('admin:cafeapp_herobanner_change', args=[banner.pk])
        home = self.client.get(reverse('cafe_list'))
        self.assertContains(home, banner.image.url)
        self.assertContains(home, 'hero__image--left')
        self.assertNotContains(home, 'class="matcha-art"')
        self.assertContains(self.client.get(url), banner.image.url)
        self.assertEqual(self.client.get(add_url).status_code, 403)
        response = self.client.post(url, {'image': self.photo('hero-new.png'), 'position': 'right', '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        banner.refresh_from_db()
        self.assertTrue(banner.image.name.endswith('hero-new.png'))
        self.assertContains(self.client.get(reverse('cafe_list')), 'hero__image--right')
        self.cafe.refresh_from_db()
        self.assertFalse(self.cafe.image)
        self.assertEqual(self.client.post(url, {'image-clear': 'on', 'position': 'center', '_save': 'Save'}).status_code, 302)
        self.assertContains(self.client.get(reverse('cafe_list')), 'class="matcha-art"')

    def test_banner_rejects_invalid_image_and_unauthorized_changes(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import HeroBanner

        url = reverse('admin:cafeapp_herobanner_add')
        self.assertEqual(self.client.post(url, {'position': 'center'}).status_code, 302)
        staff = get_user_model().objects.create_user(username='banner_staff', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.post(url, {'position': 'center'}).status_code, 403)
        self.client.force_login(self.admin_user)
        response = self.client.post(url, {'image': SimpleUploadedFile('bad.png', b'not an image'), 'position': 'center'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['adminform'].form.errors.get('image'))
        self.assertFalse(HeroBanner.objects.exists())


class CafeSearchPopupTests(TestCase):
    def setUp(self):
        base = dict(address='서울', menu_name='말차 라테', price=6500,
                    description='테스트', latitude='37.540000', longitude='127.040000',
                    sweetness=2, is_vegan=True)
        self.local = Cafe.objects.create(name='초록 카페', area='성수', image='cafes/example.png', **base)
        self.named = Cafe.objects.create(name='성수 말차', area='연남', **base)
        self.no_coords = Cafe.objects.create(name='성수 작은집', area='성수', menu_name='말차', price=5000, description='좌표 없음', address='서울')
        Cafe.objects.create(name='다른 카페', area='삼성', **base)

    def test_name_or_area_search_intersects_existing_filters(self):
        response = self.client.get(reverse('cafe_list'), {'q': ' 성수 '})
        self.assertEqual({c.pk for c in response.context['cafes']}, {self.local.pk, self.named.pk, self.no_coords.pk})
        self.assertEqual(response.context['result_count'], 3)
        self.assertEqual(len(response.context['map_cafes']), 2)
        response = self.client.get(reverse('cafe_list'), {'q': '성수', 'area': '성수', 'sweetness': 2, 'is_vegan': 'on'})
        self.assertEqual(list(response.context['cafes']), [self.local])
        self.assertEqual([c['name'] for c in response.context['map_cafes']], [self.local.name])
        self.assertEqual(self.client.get(reverse('cafe_list'), {'q': '없는검색어'}).context['result_count'], 0)

    def test_popup_aggregates_reviews_and_handles_missing_image(self):
        for index, rating in enumerate((3, 5)):
            user = get_user_model().objects.create_user(username=f'popup{index}')
            Review.objects.create(cafe=self.local, author=user, rating=rating, comment='좋아요')
        response = self.client.get(reverse('cafe_list'), {'q': '성수'})
        data = {item['name']: item for item in response.context['map_cafes']}
        popup = data[self.local.name]
        self.assertEqual(popup['average_rating'], 4)
        self.assertEqual(popup['review_count'], 2)
        self.assertEqual(popup['image_url'], self.local.image.url)
        self.assertEqual(popup['menu_name'], '말차 라테')
        self.assertEqual(popup['price'], 6500)
        self.assertEqual(popup['detail_url'], reverse('cafe_detail', args=[self.local.pk]))
        self.assertIsNone(data[self.named.name]['image_url'])
        self.assertIsNone(data[self.named.name]['average_rating'])
        self.assertEqual(data[self.named.name]['review_count'], 0)

    def test_popup_data_escapes_script_markup(self):
        self.local.name = '</script><script>alert(1)</script>'
        self.local.save()
        response = self.client.get(reverse('cafe_list'))
        self.assertNotContains(response, self.local.name)
        self.assertContains(response, r'\u003C/script\u003E')
