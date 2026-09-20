from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    CafeRecommendationForm,
    CafeSuggestionForm,
    CafeTasteFilterForm,
    ReviewForm,
)
from .models import Cafe, Favorite, Review, HeroBanner


def _favorite_cafe_ids(user):
    if not user.is_authenticated:
        return []
    return list(user.favorites.values_list('cafe_id', flat=True))


def cafe_list(request):
    areas = ['삼성', '성수', '명동', '연남', '서촌', '삼청']
    selected_area = request.GET.get('area')
    query = request.GET.get('q', '').strip()
    cafes = Cafe.objects.all()
    taste_filter_form = CafeTasteFilterForm(request.GET)

    if selected_area in areas:
        cafes = cafes.filter(area=selected_area)

    if query:
        cafes = cafes.filter(Q(name__icontains=query) | Q(area__icontains=query))

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
        'cafes': cafes,
        'hero_banner': HeroBanner.objects.first(),
        'areas': areas,
        'selected_area': selected_area,
        'query': query,
        'taste_filter_form': taste_filter_form,
        'result_count': cafes.count(),
        'map_cafes': map_cafes,
        'favorite_cafe_ids': _favorite_cafe_ids(request.user),
    }
    return render(request, 'cafeapp/cafe_list.html', context)


def cafe_detail(request, cafe_id):
    cafe = get_object_or_404(
        Cafe.objects.prefetch_related('reviews__author'),
        id=cafe_id,
    )
    favorite_cafe_ids = _favorite_cafe_ids(request.user)
    review_summary = cafe.reviews.aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id'),
    )
    has_reviewed = (
        request.user.is_authenticated
        and cafe.reviews.filter(author=request.user).exists()
    )
    return render(
        request,
        'cafeapp/cafe_detail.html',
        {
            'cafe': cafe,
            'is_favorite': cafe.id in favorite_cafe_ids,
            'reviews': cafe.reviews.all(),
            'average_rating': review_summary['average_rating'],
            'review_count': review_summary['review_count'],
            'review_form': ReviewForm(),
            'has_reviewed': has_reviewed,
        },
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
            form.save()
            return redirect('cafe_suggestion_complete')
    else:
        form = CafeSuggestionForm()

    return render(
        request,
        'cafeapp/cafe_suggestion_form.html',
        {'form': form},
    )


def cafe_suggestion_complete(request):
    return render(request, 'cafeapp/cafe_suggestion_complete.html')


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
                'matcha_strength': '진하기',
                'bitterness': '쌉싸름함',
                'sweetness': '단맛',
                'milkiness': '우유맛',
                'matcha_aroma': '말차 향',
            }
            matched_labels = [field_labels[name] for name in closest_fields[:2]]
            reason = f"{', '.join(matched_labels)}이(가) 원하는 취향과 가장 비슷해요."
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
        messages.info(request, '이 카페에는 이미 리뷰를 작성했습니다.')
        return redirect('cafe_detail', cafe_id=cafe.id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.cafe = cafe
        review.author = request.user
        review.save()
        messages.success(request, '리뷰가 등록되었습니다.')
        return redirect('cafe_detail', cafe_id=cafe.id)

    favorite_cafe_ids = _favorite_cafe_ids(request.user)
    review_summary = cafe.reviews.aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id'),
    )
    return render(
        request,
        'cafeapp/cafe_detail.html',
        {
            'cafe': cafe,
            'is_favorite': cafe.id in favorite_cafe_ids,
            'reviews': cafe.reviews.select_related('author'),
            'average_rating': review_summary['average_rating'],
            'review_count': review_summary['review_count'],
            'review_form': form,
            'has_reviewed': False,
        },
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
        messages.success(request, '리뷰가 삭제되었습니다.')
    return redirect('cafe_detail', cafe_id=cafe_id)


def signup(request):
    if request.user.is_authenticated:
        return redirect('cafe_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('cafe_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
