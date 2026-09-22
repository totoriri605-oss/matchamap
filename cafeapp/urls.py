from django.urls import path

from . import views


urlpatterns = [
    path('guide/', views.matcha_guide, name='matcha_guide'),
    path('', views.cafe_list, name='cafe_list'),
    path('cafes/', views.cafe_list, {'catalog': True}, name='cafe_catalog'),
    path(
        'recommendations/',
        views.cafe_recommendations,
        name='cafe_recommendations',
    ),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('cafes/suggest/', views.cafe_suggestion_create, name='cafe_suggestion'),
    path(
        'cafes/suggest/complete/',
        views.cafe_suggestion_complete,
        name='cafe_suggestion_complete',
    ),
    path(
        'cafes/<int:cafe_id>/favorite/',
        views.toggle_favorite,
        name='toggle_favorite',
    ),
    path(
        'cafes/<int:cafe_id>/reviews/',
        views.review_create,
        name='review_create',
    ),
    path(
        'cafes/<int:cafe_id>/reviews/<int:review_id>/delete/',
        views.review_delete,
        name='review_delete',
    ),
    path('cafes/<int:cafe_id>/', views.cafe_detail, name='cafe_detail'),
    path('accounts/signup/', views.signup, name='signup'),
]
