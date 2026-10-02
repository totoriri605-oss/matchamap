"""정적 파일(CSS 등) 주소 뒤에 파일 수정 시각을 붙여, 파일이 바뀌면 브라우저가 새로 받게 한다.

예) {% static_v 'cafeapp/home.css' %}  ->  /static/cafeapp/home.css?v=1790910000
브라우저는 주소가 같으면 옛 CSS를 오래 기억하기 때문에, 디자인을 바꿔도 화면마다 옛 모습이
남는 문제가 생긴다. 서버에 모아 둔(collectstatic) 환경에서 파일을 못 찾으면 그냥 기본 주소를 쓴다.
"""
import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_v(path):
    url = static(path)
    absolute_path = finders.find(path)
    if isinstance(absolute_path, str) and os.path.exists(absolute_path):
        return f'{url}?v={int(os.path.getmtime(absolute_path))}'
    return url
