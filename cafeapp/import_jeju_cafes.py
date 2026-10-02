"""Seed Jeju matcha cafes (2026-10-02 조사).

실행: python manage.py shell -c "from cafeapp import import_jeju_cafes as m; m.run()"

각 카페의 주소·영업시간·메뉴는 아래 SOURCES에 적은 웹 페이지에서 확인한 값만 썼다.
- 가격은 출처에 없어서 0으로 둔다(화면에는 '가격 정보 확인 중'으로 표시).
- 좌표는 OpenStreetMap Nominatim에서 주소/건물명이 일치한 곳만 넣었고,
  나머지는 틀린 위치를 넣지 않도록 비워 두었다(카드 목록에는 보이고 지도 마커만 없음).
- 이미 있는 카페(이름+동네 동일)는 새로 만들지 않고 건너뛴다.
"""
from decimal import Decimal

from django.db import transaction

from cafeapp.models import Cafe

SOURCES = {
    '글로시말차': 'https://www.st-news.co.kr/news/articleView.html?idxno=9806 (2024-05-10)',
    '애월말차': 'https://wanderlog.com/place/details/5925873/aewol-matcha',
    '슬로우 말차': 'https://sa.trip.com/moments/detail/seogwipo-14755-146326301?locale=en-SA',
    '산노루 제주': 'https://world.nol.com/en/content/pois/e16bf130-075f-4fa6-8a1b-35f8c8744139',
    '오설록 티뮤지엄': 'https://www.osulloc.com/kr/ko/store-introduction/jeju-map',
    '무상찻집': 'https://www.st-news.co.kr/news/articleView.html?idxno=9806',
}

NEW_CAFES = [
    dict(
        name='글로시말차', country='KR', city='jeju', area='조천',
        address='제주 제주시 조천읍 조함해안로 112 1층',
        menu_name='말차 라테', price=0,
        description='조천 해안도로 옆의 말차 카페로, 말차 라테·말차 스트레이트·말차 테린느 등 말차 디저트를 냅니다.',
        business_hours='매일 10:30~18:30 (라스트오더 18:00)',
    ),
    dict(
        name='애월말차', country='KR', city='jeju', area='애월',
        address='제주 제주시 애월읍 하광로 183',
        menu_name='말차 빙수', price=0,
        description='애월의 차밭이 내려다보이는 말차 카페로, 팥을 직접 만들어 올린 말차 빙수와 말차 라테, 크로플이 알려져 있습니다.',
        business_hours='11:00~18:00 (화요일 휴무)',
    ),
    dict(
        name='슬로우 말차', country='KR', city='jeju', area='중문',
        address='제주 서귀포시 1100로 453-95 2층',
        latitude=Decimal('33.286219'), longitude=Decimal('126.444266'),
        menu_name='직접 격불한 말차', price=0,
        description='위호텔 제주에 있는 말차 카페로, 제주 화산암반수와 말차를 티 텐더가 직접 격불해 내며 말차 디저트도 함께 즐길 수 있습니다.',
        business_hours='',
    ),
    dict(
        name='산노루 제주', country='KR', city='jeju', area='한경',
        address='제주 제주시 한경면 낙원로 32',
        menu_name='말차 음료와 베이커리', price=0,
        description='흰색 인테리어와 식물이 어우러진 말차 카페 & 베이커리로, 오설록 티뮤지엄에서 차로 약 11분 거리입니다.',
        business_hours='10:00~19:00',
    ),
    dict(
        name='오설록 티뮤지엄', country='KR', city='jeju', area='안덕',
        address='제주 서귀포시 신화역사로 15',
        latitude=Decimal('33.305366'), longitude=Decimal('126.288022'),
        menu_name='말차 라테 / 말차 롤케이크', price=0,
        description='오설록의 제주 대표 매장으로 차밭 전망의 카페에서 말차 라테와 말차 롤케이크, 티테라스의 말차 국수를 맛볼 수 있습니다.',
        business_hours='연중무휴 09:00~18:00 (하절기 19:00)',
    ),
]

# 기존 무상찻집(ID 19)의 비어 있던 주소와 영업시간만 채운다.
MUSANG_UPDATE = dict(
    area='용담',
    address='제주 제주시 서광로5길 10 단독주택',
    business_hours='목~월 11:00~18:00 (화·수 휴무)',
)


@transaction.atomic
def run():
    created = []
    skipped = []
    for data in NEW_CAFES:
        if Cafe.objects.filter(name=data['name'], city=data['city']).exists():
            skipped.append(data['name'])
            continue
        cafe = Cafe(**data)
        cafe.full_clean(exclude=['image'])
        cafe.save()
        created.append(cafe.name)
        print('CREATED', cafe.pk, cafe.name)

    updated = False
    musang = Cafe.objects.filter(name='무상찻집', city='jeju').first()
    if musang and musang.address == '방문 지점과 주소 확인 중':
        for field, value in MUSANG_UPDATE.items():
            setattr(musang, field, value)
        musang.full_clean(exclude=['image'])
        musang.save()
        updated = True
        print('UPDATED', musang.pk, musang.name)

    print(f'done: created={created} skipped={skipped} musang_updated={updated}')
