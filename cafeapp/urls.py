from django.urls import path

from . import views


urlpatterns = [
    path('', views.cafe_list, name='cafe_list'),
    path('cafes/<int:cafe_id>/', views.cafe_detail, name='cafe_detail'),
]
