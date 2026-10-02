from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import quote
from django.utils.translation import get_language, gettext as _

from .forms import (
    CafeRecommendationForm,
    CafeSuggestionForm,
    CafeTasteFilterForm,
    ReviewForm,
)
from .models import Cafe, Favorite, Review, HeroBanner
from .locations import COUNTRIES, CITIES
from .guide_content import GUIDE_ARTICLES, GUIDE_REGIONS


def matcha_guide(request):
    return render(request, 'cafeapp/matcha_guide.html', {
        'is_guide': True,
        'guide_articles': GUIDE_ARTICLES,
        'guide_regions': GUIDE_REGIONS,
    })


def _favorite_cafe_ids(user):
    if not user.is_authenticated:
        return []
    return list(user.favorites.values_list('cafe_id', flat=True))


def cafe_list(request, catalog=False):
    selected_country = request.GET.get('country', 'KR')
    if selected_country not in COUNTRIES:
        selected_country = 'KR'
    selected_city = request.GET.get('city')
    if selected_city not in CITIES or CITIES[selected_city]['country'] != selected_country:
        selected_city = next(key for key, value in CITIES.items() if value['country'] == selected_country)
    areas = ['삼성', '성수', '명동', '연남', '서촌', '삼청']
    selected_area = request.GET.get('area')
    query = request.GET.get('q', '').strip()
    is_pick_filter_active = request.GET.get('pick') == '1'
    cafes = Cafe.objects.filter(country=selected_country, city=selected_city)
    if selected_city != 'seoul':
        areas = list(cafes.order_by('area').values_list('area', flat=True).distinct())
    if selected_area not in areas:
        selected_area = None
    def location_url(country, city):
        params = request.GET.copy()
        params.pop('area', None)
        params['country'] = country
        params['city'] = city
        return '?' + params.urlencode()
    city_grid_choices = [
        {
            'code': code,
            'name': value['name'],
            'name_en': value['name_en'],
            'url': location_url(value['country'], code),
            'image': f'cafeapp/cities/{code}.jpg',
        }
        for code, value in CITIES.items()
    ]
    taste_filter_form = CafeTasteFilterForm(request.GET)

    if selected_area in areas:
        cafes = cafes.filter(area=selected_area)

    if query:
        cafes = cafes.filter(Q(name__icontains=query) | Q(area__icontains=query))

    if is_pick_filter_active:
        cafes = cafes.filter(is_matchayojung_pick=True)

    if taste_filter_form.is_valid():
        taste_filters = {}
        filter_lookups = {
            'matcha_strength': 'matcha_strength__gte',
            'bitterness': 'bitterness__gte',
            'sweetness': 'sweetness__lte',
            'milkiness': 'milkiness__lte',
            'matcha_aroma': 'matcha_aroma__gte',
        }
        for field_name, lookup in filter_lookups.items():
            value = taste_filter_form.cleaned_data[field_name]
            if value is not None:
                taste_filters[lookup] = value

        for field_name in (
            'is_decaf',
            'is_vegan',
            'has_parking',
            'has_takeout',
        ):
            if taste_filter_form.cleaned_data[field_name]:
                taste_filters[field_name] = True

        cafes = cafes.filter(**taste_filters)

    cafes = cafes.annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews'))

    map_cafes = [
        {
            'name': cafe.name,
            'is_pick': cafe.is_matchayojung_pick,
            'area': cafe.area,
            'menu_name': cafe.menu_name,
            'price': cafe.price,
            'image_url': cafe.image.url if cafe.image else None,
            'average_rating': cafe.average_rating,
            'review_count': cafe.review_count,
            'latitude': cafe.latitude,
            'longitude': cafe.longitude,
            'detail_url': reverse('cafe_detail', args=[cafe.id]),
        }
        for cafe in cafes.filter(
            latitude__isnull=False,
            longitude__isnull=False,
        )
    ]

    context = {
        'is_catalog': catalog,
        'cafes': cafes,
        'selected_country': selected_country,
        'selected_city': selected_city,
        'city_name': CITIES[selected_city]['name_en' if (get_language() or '').startswith('en') else 'name'],
        'city_bounds': CITIES[selected_city]['bounds'],
        'city_grid_choices': city_grid_choices,
        'hero_banner': HeroBanner.objects.first(),
        'areas': areas,
        'selected_area': selected_area,
        'query': query,
        'is_pick_filter_active': is_pick_filter_active,
        'taste_filter_form': taste_filter_form,
        'result_count': cafes.count(),
        'map_cafes': map_cafes,
        'favorite_cafe_ids': _favorite_cafe_ids(request.user),
    }
    template = 'cafeapp/cafe_catalog.html' if catalog else 'cafeapp/cafe_list.html'
    return render(request, template, context)


def _cafe_detail_context(request, cafe, review_form, reviews, has_reviewed):
    """카페 상세 화면(정상 조회와 리뷰 입력 오류 재표시)이 함께 쓰는 데이터."""
    review_summary = cafe.reviews.aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id'),
    )
    taste_fields = (
        ('matcha_strength', _('진하기')),
        ('bitterness', _('쌉싸름함')),
        ('sweetness', _('단맛')),
        ('milkiness', _('우유맛')),
        ('matcha_aroma', _('말차 향')),
    )
    place_query = quote(f'{cafe.name} {cafe.address}')
    directions = [{'name': _('구글 지도'), 'url': f'https://www.google.com/maps/search/?api=1&query={place_query}'}]
    if cafe.country == 'KR':
        directions.append({'name': _('네이버 지도'), 'url': f'https://map.naver.com/p/search/{place_query}'})
    city = CITIES.get(cafe.city)
    is_english = (get_language() or '').startswith('en')
    return {
        'is_catalog': True,  # 머리글에서 '카페 목록' 메뉴를 강조한다.
        'is_detail': True,   # 머리글 검색 아이콘이 카페 목록 검색으로 이동한다.
        'city_name': (city['name_en'] if is_english else city['name']) if city else '',
        'cafe': cafe,
        'is_favorite': cafe.id in _favorite_cafe_ids(request.user),
        'reviews': reviews,
        'average_rating': review_summary['average_rating'],
        'review_count': review_summary['review_count'],
        'review_form': review_form,
        'has_reviewed': has_reviewed,
        'taste_rows': [
            {'label': label, 'value': getattr(cafe, field)}
            for field, label in taste_fields
            if getattr(cafe, field)
        ],
        'unset_taste_labels': [label for field, label in taste_fields if not getattr(cafe, field)],
        'taste_levels': range(1, 6),
        'directions': directions,
    }


def cafe_detail(request, cafe_id):
    cafe = get_object_or_404(
        Cafe.objects.prefetch_related('reviews__author'),
        id=cafe_id,
    )
    has_reviewed = (
        request.user.is_authenticated
        and cafe.reviews.filter(author=request.user).exists()
    )
    return render(
        request,
        'cafeapp/cafe_detail.html',
        _cafe_detail_context(request, cafe, ReviewForm(), cafe.reviews.all(), has_reviewed),
    )


@login_required
def toggle_favorite(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)

    if request.method == 'POST':
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            cafe=cafe,
        )
        if not created:
            favorite.delete()

    next_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('cafe_detail', args=[cafe.id])

    return redirect(next_url)


@login_required
def favorite_list(request):
    favorite_cafe_ids = _favorite_cafe_ids(request.user)
    cafes = Cafe.objects.filter(id__in=favorite_cafe_ids)
    return render(
        request,
        'cafeapp/favorite_list.html',
        {
            'cafes': cafes,
            'favorite_cafe_ids': favorite_cafe_ids,
        },
    )


def cafe_suggestion_create(request):
    if request.method == 'POST':
        form = CafeSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save()
            request.session['last_suggestion_name'] = suggestion.name
            return redirect('cafe_suggestion_complete')
    else:
        form = CafeSuggestionForm()

    return render(
        request,
        'cafeapp/cafe_suggestion_form.html',
        {'form': form},
    )


def cafe_suggestion_complete(request):
    # 방금 제보한 카페 이름은 한 번만 보여준다(새로고침하면 일반 문구).
    suggestion_name = request.session.pop('last_suggestion_name', None)
    return render(request, 'cafeapp/cafe_suggestion_complete.html', {
        'suggestion_name': suggestion_name,
    })


def cafe_recommendations(request):
    form = CafeRecommendationForm(request.GET or None)
    recommendations = []

    if form.is_valid():
        taste_fields = (
            'matcha_strength',
            'bitterness',
            'sweetness',
            'milkiness',
            'matcha_aroma',
        )
        cafes = Cafe.objects.all()
        for field_name in taste_fields:
            cafes = cafes.filter(**{f'{field_name}__isnull': False})

        for field_name in (
            'is_decaf',
            'is_vegan',
            'has_parking',
            'has_takeout',
        ):
            if form.cleaned_data[field_name]:
                cafes = cafes.filter(**{field_name: True})

        ranked_cafes = []
        for cafe in cafes:
            differences = {
                field_name: abs(
                    getattr(cafe, field_name) - form.cleaned_data[field_name]
                )
                for field_name in taste_fields
            }
            distance = sum(differences.values())
            closest_fields = [
                field_name
                for field_name, difference in differences.items()
                if difference == min(differences.values())
            ]
            field_labels = {
                'matcha_strength': _('진하기'),
                'bitterness': _('쌉싸름함'),
                'sweetness': _('단맛'),
                'milkiness': _('우유맛'),
                'matcha_aroma': _('말차 향'),
            }
            matched_labels = [field_labels[name] for name in closest_fields[:2]]
            reason = _('%(labels)s이(가) 원하는 취향과 가장 비슷해요.') % {'labels': ', '.join(matched_labels)}
            ranked_cafes.append(
                {
                    'cafe': cafe,
                    'distance': distance,
                    'match_percentage': round((1 - distance / 20) * 100),
                    'reason': reason,
                }
            )

        recommendations = sorted(
            ranked_cafes,
            key=lambda item: (item['distance'], item['cafe'].id),
        )[:3]

    return render(
        request,
        'cafeapp/cafe_recommendations.html',
        {
            'form': form,
            'recommendations': recommendations,
            'favorite_cafe_ids': _favorite_cafe_ids(request.user),
        },
    )


@login_required
def review_create(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)

    if request.method != 'POST':
        return redirect('cafe_detail', cafe_id=cafe.id)

    if Review.objects.filter(cafe=cafe, author=request.user).exists():
        messages.info(request, _('이 카페에는 이미 리뷰를 작성했습니다.'))
        return redirect('cafe_detail', cafe_id=cafe.id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.cafe = cafe
        review.author = request.user
        review.save()
        messages.success(request, _('리뷰가 등록되었습니다.'))
        return redirect('cafe_detail', cafe_id=cafe.id)

    return render(
        request,
        'cafeapp/cafe_detail.html',
        _cafe_detail_context(request, cafe, form, cafe.reviews.select_related('author'), False),
        status=400,
    )


@login_required
def review_delete(request, cafe_id, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        cafe_id=cafe_id,
        author=request.user,
    )
    if request.method == 'POST':
        review.delete()
        messages.success(request, _('리뷰가 삭제되었습니다.'))
    return redirect('cafe_detail', cafe_id=cafe_id)


def signup(request):
    if request.user.is_authenticated:
        return redirect('cafe_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 인증 백엔드가 2개(ModelBackend, allauth)라서 어느 쪽으로 로그인할지 지정해야 한다.
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, _('회원가입이 완료되었습니다.'))
            return redirect('cafe_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
