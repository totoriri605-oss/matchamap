"""Editorial guide content, separate from Cafe data. Slugs are stable link targets.

Images illustrate the content; they do not document a cafe or tea origin.
Later, article links can point to detail views without changing the page layout.
"""

GUIDE_ARTICLES = [
    {
        'slug': 'basics', 'category': '말차 입문', 'category_description': '말차란? / 녹차와의 차이',
        'title': '말차 초보자를 위한 첫 가이드',
        'description': '말차가 처음이라도 괜찮아요. 한 잔을 이해하는 작은 이야기부터 시작해요.',
        'image': 'cafeapp/guide/ritual.png', 'tags': ['말차기초', '녹차와의차이', '초보자추천'],
        'paragraphs': [
            '말차도 녹차의 한 종류예요. 햇빛을 가려 재배한 찻잎으로 만든 텐차를 곱게 갈아 가루로 만듭니다. 잎을 물에 우린 뒤 건져내는 차와 달리, 말차는 가루를 물에 풀어 함께 마셔요.',
            '처음에는 한 모금씩 천천히 마시며 향과 여운을 느껴보세요. 라떼를 고른다면 시럽을 따로 요청해, 자신에게 편안한 단맛을 찾아보는 것도 좋아요.',
        ],
        'source_url': 'https://ippodotea.com/collections/matcha', 'source_label': 'Ippodo · 말차 소개',
    },
    {
        'slug': 'flavor', 'category': '맛 이해하기', 'category_description': '진하기, 쌉싸름함, 단맛, 향',
        'title': '진한 말차와 부드러운 말차의 차이',
        'description': '진하면 꼭 쓴 걸까요? 맛의 여러 얼굴을 따로 느껴보세요.',
        'image': 'cafeapp/guide/comparison.png', 'tags': ['맛의차이', '진하기', '쌉싸름함'],
        'paragraphs': [
            '진하기와 쌉싸름함은 같은 뜻이 아니에요. 풍부한 감칠맛과 긴 여운을 가지면서도 쓴맛은 적은 말차가 있습니다. 원료와 블렌딩에 따라서도 맛의 인상이 달라져요.',
            '카페에서는 “말차 맛은 진하게, 단맛은 적게”처럼 원하는 특징을 나눠 말해보세요. 진하기·단맛·향을 각각 살펴보면 내 취향을 더 쉽게 설명할 수 있어요.',
        ],
        'source_url': 'https://ippodotea.com/blogs/ippodo-tea-blog/what-is-the-difference-between-our-matcha-blends-part-i',
        'source_label': 'Ippodo · 말차 블렌드의 차이',
    },
    {
        'slug': 'menu', 'category': '메뉴 가이드', 'category_description': '라떼, 스트레이트, 디저트',
        'title': '말차 라떼 vs 스트레이트 말차',
        'description': '우유와 함께 부드럽게, 또는 차의 향에 집중하며. 오늘의 한 잔을 골라요.',
        'image': 'cafeapp/guide/latte.png', 'tags': ['말차라떼', '스트레이트', '메뉴비교'],
        'paragraphs': [
            '라떼는 말차에 우유를 더한 메뉴, 스트레이트는 우유 없이 물로 풀어 즐기는 메뉴예요. 같은 말차라도 우유와 시럽을 더하면 다른 한 잔이 됩니다.',
            '차 자체의 향을 느끼고 싶은 날에는 스트레이트를, 우유의 고소함과 함께 즐기고 싶은 날에는 라떼를 골라보세요. 말차는 케이크나 아이스크림 같은 디저트로도 만날 수 있어요.',
            '우유 종류와 시럽의 기본 포함 여부는 카페마다 달라요. 주문 전에 물어보면 원하는 맛에 한 걸음 더 가까워집니다.',
        ],
    },
    {
        'slug': 'choosing', 'category': '좋은 말차 고르기', 'category_description': '색, 향, 등급, 보관법',
        'title': '좋은 말차를 고르는 5가지 기준',
        'description': '색과 향부터 용도와 보관까지. 나에게 맞는 말차를 천천히 찾아봐요.',
        'image': 'cafeapp/guide/powder.png', 'tags': ['말차고르기', '등급', '보관법'],
        'paragraphs': [
            '① 색: 사진의 초록색만으로 품질을 단정하지 말고 제품 설명도 함께 읽어요. ② 향: 직접 맛볼 수 있다면 어떤 향이 편안하게 느껴지는지 살펴봐요.',
            '③ 용도: 물에 풀어 마실지, 라떼나 베이킹에 사용할지 먼저 생각해요. ④ 제품 정보: 원재료와 제조사의 설명을 확인해요. “세리머니얼” 같은 등급 이름 하나만으로 제품을 판단하지 않아요.',
            '⑤ 보관: 제조사 안내를 따르되, 빛이 들지 않는 밀폐 용기를 사용하고 열과 강한 냄새를 피해요. 개봉일을 적어두면 신선하게 즐기는 데 도움이 됩니다.',
        ],
        'source_url': 'https://ippodotea.com/blogs/ippodo-tea-blog/how-to-keep-your-matcha-fresh',
        'source_label': 'Ippodo · 보관 안내',
        'extra_source_url': 'https://ippodotea.com/blogs/frequently-asked-questions',
        'extra_source_label': 'Ippodo · 등급 관련 FAQ',
    },
]

GUIDE_TASTES = [
    {'name': '말차 진하기', 'description': '한 모금에 느껴지는 말차의 존재감', 'low': '연함', 'high': '진함'},
    {'name': '쌉싸름함', 'description': '입안에 남는 쌉싸름한 느낌', 'low': '적음', 'high': '많음'},
    {'name': '단맛', 'description': '음료에서 느껴지는 달콤함', 'low': '적음', 'high': '많음'},
    {'name': '우유맛', 'description': '차와 어우러지는 우유의 고소함', 'low': '가벼움', 'high': '진함'},
    {'name': '말차 향', 'description': '코끝과 입안에 머무는 차의 향', 'low': '은은함', 'high': '풍부함'},
]

GUIDE_REGIONS = [
    {'name': '우지', 'label': 'KYOTO', 'description': '교토의 차 문화를 알아보는 출발점.', 'image': 'cafeapp/guide/fields.png', 'url': 'https://www.japan.travel/en/spot/2017/'},
    {'name': '니시오', 'label': 'AICHI', 'description': '아이치의 말차 산지 이야기를 만나보세요.', 'image': 'cafeapp/guide/fields.png', 'url': 'https://japan-food.jetro.go.jp/greentea/business/japanese_greentea_brochure.pdf'},
    {'name': '야메', 'label': 'FUKUOKA', 'description': '후쿠오카에서 이어지는 차의 이야기.', 'image': 'cafeapp/guide/fields.png', 'url': 'https://www.japan.travel/en/local-specialities/local-foods/'},
    {'name': '시즈오카', 'label': 'SHIZUOKA', 'description': '차로 알려진 시즈오카를 알아봐요.', 'image': 'cafeapp/guide/fields.png', 'url': 'https://www.japan.travel/en/destinations/tokai/shizuoka/'},
    {'name': '서울', 'label': 'SEOUL', 'description': '산지 밖, 일상에서 즐기는 말차 카페 문화.', 'image': 'cafeapp/cities/seoul.jpg', 'local': True},
]
