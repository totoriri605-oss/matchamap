"""Import the owner's supplied blog index; do not infer reviews or branch coordinates."""
from django.db import transaction
from cafeapp.models import Cafe

POSTS = [
    ('Blank Street', 'US', 'new-york', '뉴욕', '말차', '224395490474'),
    ('무상찻집', 'KR', 'jeju', '제주', '유기농 말차라떼', '224045286019'),
    ('더기와', 'KR', 'seoul', '합정', '말차막걸리', '224021596480'),
    ('아우프글렛 한남', 'KR', 'seoul', '한남', '말차크로플', '224010824869'),
    ('티노마드', 'KR', 'seoul', '망원', '말차빙수', '223938880255'),
    ('롱베케이션', 'KR', 'seoul', '연남', '말차푸딩', '223933290441'),
    ('Ogawa Coffee', 'US', 'boston', '보스턴', '말차라떼', '223872780177'),
    ('12 Matcha', 'US', 'new-york', 'NoHo', 'Matcha Latte', '223871241826'),
    ('Cha Cha Matcha', 'US', 'new-york', '뉴욕', '말차', '223778806733'),
]


@transaction.atomic
def run():
    for name, country, city, area, menu, post in POSTS:
        url = f'https://blog.naver.com/hjmo-o/{post}'
        cafe = Cafe.objects.filter(blog_url=url).first()
        if cafe is None:
            cafe = Cafe.objects.filter(name=name, country=country, city=city).first()
        if cafe is not None:
            if cafe.blog_url and cafe.blog_url != url:
                raise ValueError(f'Existing review differs: {name}')
            cafe.blog_url = url
            cafe.save(update_fields=['blog_url'])
            print('LINKED', cafe.pk, name)
        else:
            cafe = Cafe.objects.create(
                name=name, country=country, city=city, area=area,
                address='방문 지점과 주소 확인 중', menu_name=menu, price=0,
                description='방문 후기 목록에서 등록한 장소입니다. 메뉴는 글 제목 기준이며 현재 판매 여부와 가격은 확인 중입니다.',
                blog_url=url,
            )
            print('CREATED', cafe.pk, name)
