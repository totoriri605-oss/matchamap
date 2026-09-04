from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Cafe


def cafe_list(request):
    areas = ['삼성', '성수', '명동', '연남', '서촌', '삼청']
    selected_area = request.GET.get('area')
    query = request.GET.get('q', '').strip()
    cafes = Cafe.objects.all()

    if selected_area in areas:
        cafes = cafes.filter(area=selected_area)

    if query:
        cafes = cafes.filter(name__icontains=query)

    map_cafes = [
        {
            'name': cafe.name,
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
        'areas': areas,
        'selected_area': selected_area,
        'query': query,
        'map_cafes': map_cafes,
    }
    return render(request, 'cafeapp/cafe_list.html', context)


def cafe_detail(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    return render(request, 'cafeapp/cafe_detail.html', {'cafe': cafe})
