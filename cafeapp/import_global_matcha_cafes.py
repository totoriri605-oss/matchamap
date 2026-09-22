"""Seed real matcha cafes for Tokyo, Osaka, and San Francisco.

Addresses were cross-checked against 2-3 travel/food sources each and
geocoded via OpenStreetMap Nominatim. Prices were not consistently
published by the sources, so price is left at 0 (shown as "가격 정보
확인 중" in the UI) rather than guessed.
"""
from decimal import Decimal

from django.db import transaction

from cafeapp.models import Cafe

CAFES = [
    dict(
        name='Higashiya Ginza', country='JP', city='tokyo', area='긴자',
        address='POLA Ginza Building 2F, 1-7-7 Ginza, Chuo-ku, Tokyo',
        latitude=Decimal('35.672014'), longitude=Decimal('139.764720'),
        menu_name='계절 화과자 + 말차 세트', price=0,
        description='긴자의 조용한 티살롱으로 30여 종의 일본차와 계절 화과자를 페어링해서 냅니다.',
        business_hours='',
    ),
    dict(
        name='The Matcha Tokyo 오모테산도점', country='JP', city='tokyo', area='오모테산도',
        address='5-11-13 Jingumae, Shibuya-ku, Tokyo 150-0001',
        latitude=Decimal('35.666932'), longitude=Decimal('139.706480'),
        menu_name='말차 코코넛 플로트', price=0,
        description='오모테산도의 말차 전문 카페로, 세레모니얼 등급 말차와 코코넛 플로트 음료로 잘 알려져 있습니다.',
        business_hours='',
    ),
    dict(
        name='나카무라 토키치 긴자식스점', country='JP', city='tokyo', area='긴자',
        address='GINZA SIX 4F, 6-10-1 Ginza, Chuo-ku, Tokyo',
        latitude=Decimal('35.669533'), longitude=Decimal('139.764049'),
        menu_name='나마차 젤리 "후카미도리"', price=0,
        description='1854년 교토 우지에서 시작한 말차 브랜드의 도쿄 유일 매장으로, 나마차 젤리가 대표 메뉴입니다.',
        business_hours='',
    ),
    dict(
        name='사료 츠지리 다이마루도쿄점', country='JP', city='tokyo', area='마루노우치',
        address='Daimaru Tokyo 10F, 1-9-1 Marunouchi, Chiyoda-ku, Tokyo',
        latitude=Decimal('35.681083'), longitude=Decimal('139.768586'),
        menu_name='말차 파르페', price=0,
        description='다이마루 도쿄 백화점 10층의 말차 디저트 전문점으로, 말차 파르페가 인기입니다.',
        business_hours='',
    ),
    dict(
        name='Nanaya 아오야마', country='JP', city='tokyo', area='시부야',
        address='2-7-12 Shibuya, Shibuya-ku, Tokyo',
        latitude=Decimal('35.683880'), longitude=Decimal('139.683258'),
        menu_name='말차 젤라또 No.7', price=0,
        description='세계에서 가장 진한 말차 젤라또로 알려진 No.7 등급 젤라또를 선보이는 매장입니다.',
        business_hours='',
    ),
    dict(
        name='차료 유리 다이마루우메다점', country='JP', city='osaka', area='우메다',
        address='Daimaru Umeda 11F, 3-1-1 Umeda, Kita-ku, Osaka',
        latitude=Decimal('34.700833'), longitude=Decimal('135.493882'),
        menu_name='말차 파르페 / 말차 카키고리', price=0,
        description='다이마루 우메다 백화점 11층 다과 코너로, 말차 파르페와 카키고리를 즐길 수 있습니다.',
        business_hours='10:00~20:00',
    ),
    dict(
        name='CAFE Osaka Chakai', country='JP', city='osaka', area='텐진바시',
        address='1F, 2-1-25 Tenjinbashi, Kita-ku, Osaka 530-0041',
        latitude=Decimal('34.709842'), longitude=Decimal('135.511904'),
        menu_name='브레드토스트 말차 소프트크림', price=0,
        description='일본차 네 종류를 전문으로 다루는 카페로, 영어 메뉴와 응대가 가능합니다.',
        business_hours='13:00~18:00',
    ),
    dict(
        name='우지엔 킷사코 한큐산반가이점', country='JP', city='osaka', area='우메다',
        address='Hankyu Sanbangai South Bldg B2F, 1-1-3 Shibata, Kita-ku, Osaka',
        latitude=Decimal('34.706436'), longitude=Decimal('135.497775'),
        menu_name='말차 카키고리', price=0,
        description='한큐산반가이 쇼핑센터 내 찻집으로, 말차 카키고리가 인기 메뉴입니다.',
        business_hours='10:00~21:00',
    ),
    dict(
        name='Maccha House 난바워크점', country='JP', city='osaka', area='난바',
        address='Namba Walk B2, 2-1-15 Sennichimae, Chuo-ku, Osaka',
        latitude=Decimal('34.667071'), longitude=Decimal('135.502309'),
        menu_name='말차 티라미수', price=0,
        description='난바워크 지하상가의 말차 전문 카페로, 층층이 쌓은 말차 티라미수로 유명합니다.',
        business_hours='',
    ),
    dict(
        name='Constance Tea & Matcha', country='US', city='san-francisco', area='아우터리치먼드',
        address='3512 Balboa St, San Francisco, CA 94121',
        latitude=Decimal('37.775835'), longitude=Decimal('-122.496512'),
        menu_name='Pure Matcha', price=0,
        description='발보아 스트리트에서 돌절구로 말차를 매일 직접 갈아 내리는 카페입니다.',
        business_hours='',
    ),
    dict(
        name='Maruwu Seicha', country='US', city='san-francisco', area='재팬타운',
        address='1737 Post St #368, San Francisco, CA 94115',
        latitude=Decimal('37.785008'), longitude=Decimal('-122.430060'),
        menu_name='딸기 말차라떼', price=0,
        description='재팬타운 내 찻집으로, 홋카이도 우유를 활용한 딸기 말차라떼가 대표 메뉴입니다.',
        business_hours='',
    ),
    dict(
        name='The Mess Hall', country='US', city='san-francisco', area='프레시디오',
        address='201 Halleck St, San Francisco, CA 94129',
        latitude=Decimal('37.802607'), longitude=Decimal('-122.454658'),
        menu_name='Hot Matcha Latte', price=8,
        description='프레시디오 터널탑스 공원 내 카페로, 뉴욕의 말차 브랜드 Matchaful 원두를 사용합니다.',
        business_hours='07:00~',
    ),
    dict(
        name='Jandii', country='US', city='san-francisco', area='선셋',
        address='1100 Taraval St, San Francisco, CA 94116',
        latitude=Decimal('37.743031'), longitude=Decimal('-122.477997'),
        menu_name='Iced Matcha Einspänner', price=0,
        description='선셋 지구의 카페로, 아이스 말차 아인슈페너가 인기 메뉴입니다.',
        business_hours='',
    ),
    dict(
        name='Sōhn', country='US', city='san-francisco', area='도그패치',
        address='2535 3rd St, San Francisco, CA 94107',
        latitude=Decimal('37.757373'), longitude=Decimal('-122.388040'),
        menu_name='시그니처 크림탑 말차', price=0,
        description='도그패치의 카페로, 시그니처 크림탑 말차로 알려져 있습니다.',
        business_hours='',
    ),
]


@transaction.atomic
def run():
    created_count = 0
    skipped = []
    for data in CAFES:
        if Cafe.objects.filter(name=data['name'], area=data['area']).exists():
            skipped.append(data['name'])
            continue
        cafe = Cafe(**data)
        cafe.full_clean(exclude=['image'])
        cafe.save()
        created_count += 1
        print('CREATED', cafe.pk, cafe.name)
    print(f'done: created={created_count} skipped={skipped}')
