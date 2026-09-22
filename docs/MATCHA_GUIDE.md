# 말차 가이드 페이지

## 구조와 동작

- 주소: `/guide/`, URL 이름: `matcha_guide`.
- 기존 `cafe_list.html`의 헤더와 외곽 레이아웃을 상속한다. 가이드에서는 지도 스크립트를 불러오지 않는다.
- 공통 메뉴는 지도 / 카페 목록 / 말차 가이드 / 카페 제보 순서다. 현재 메뉴만 강조한다.
- 카테고리는 해당 글 카드로 이동하고, 글 카드는 HTML details/summary로 펼쳐 읽는다. 별도 JavaScript 없이 키보드로도 조작할 수 있다.
- 취향 1~5 단계는 설명용이다. 실제 입력과 추천은 기존 `/recommendations/`에서 제공하며 계산 규칙은 바꾸지 않았다.
- 헤더 검색은 `/cafes/#search-input`, 하단 CTA는 `/cafes/`로 연결한다.
- 일본 지역은 공식 외부 안내, 서울은 서울 카페 목록으로 연결한다. 외부 링크는 새 탭으로 열고 noopener noreferrer를 적용한다.
- `guide_content.py`에서 글과 지역, 취향 설명을 관리한다. DB와 Cafe 모델은 변경하지 않는다. 추후 상세 페이지가 생기면 안정적인 slug를 활용할 수 있다.
- 스타일은 `.matcha-guide`와 `guide-` 이름으로 분리했다. 1050px 이하 2~3열, 640px 이하 1~2열로 바뀐다.
- 언어 선택 기능은 그대로 유지한다. 이번에 작성한 가이드 본문은 한국어이며 영문 번역은 별도 작업이다.

## 확인 기록

- 자동 테스트 57개 통과, 모델 변경 없음 확인.
- Chromium에서 1440px, 768px, 390px, 320px 너비 가로 넘침 없음.
- 가이드 이미지 로딩, 글 클릭·키보드 펼치기, 현재 메뉴 표시, 검색 이동 확인.
- 지도·목록 페이지에서 서울 카드 19개 유지 확인. 제한된 점검 환경에서는 외부 Leaflet 다운로드가 차단됐으나, 네트워크 제한 밖에서 재확인하여 Leaflet 로딩과 마커 14개 생성 확인. 모든 배경 타일 다운로드 완료까지 검증한 것은 아니다.
- [PC 화면](images/matcha-guide-desktop.png), [모바일 화면](images/matcha-guide-mobile.png).

## 콘텐츠 참고 자료

- [Ippodo 말차 소개](https://ippodotea.com/collections/matcha)
- [Ippodo 블렌드의 차이](https://ippodotea.com/blogs/ippodo-tea-blog/what-is-the-difference-between-our-matcha-blends-part-i)
- [Ippodo 보관법](https://ippodotea.com/blogs/ippodo-tea-blog/how-to-keep-your-matcha-fresh)
- [Ippodo FAQ](https://ippodotea.com/blogs/frequently-asked-questions)
- [JETRO 일본 차 안내](https://japan-food.jetro.go.jp/greentea/business/japanese_greentea_brochure.pdf)
- [JNTO 우지](https://www.japan.travel/en/spot/2017/), [지역 음식](https://www.japan.travel/en/local-specialities/local-foods/), [시즈오카](https://www.japan.travel/en/destinations/tokai/shizuoka/)

지역 이름만으로 맛을 단정하지 않는다. 서울은 차 산지가 아니라 카페 문화로 소개한다. 사진 속 두 잔은 실제 농도 비교 실험이 아니다.

## 이미지 제작 기록

내장 image_gen 도구 사용. imagegen 스킬에 따라 생성 후 프로젝트로 복사했다. 모두 `cafeapp/static/cafeapp/guide/`에 저장했다. 원본은 보존했다. 생성 이미지는 실제 카페·산지 사진으로 표시하지 않는다.

- `latte.png`: 기존 `media/hero/matcha-latte-hero.png`를 복사하여 재사용. 기존 파일은 변경하지 않았다.
- 서울 이미지는 기존 `cafeapp/static/cafeapp/cities/seoul.jpg`를 재사용한다.

### 최종 생성 프롬프트

#### ritual.png

Use case: photorealistic-natural. Asset type: wide editorial hero photograph for a soft Korean matcha guide website. Primary request: a handmade cream ceramic bowl of freshly whisked matcha, bamboo chasen and a small dish of fine matcha powder on pale wood, a few green tea leaves, warm soft morning light, cream and sage green palette. Composition: landscape 3:2, bowl at right of center, gentle uncluttered cream background on left. Natural realistic textures, understated and inviting, not commercial packaging. No text, no lettering, no watermark, no UI, no logos.

#### comparison.png

Use case: photorealistic-natural. Asset type: wide 3:2 editorial photo for matcha taste guide. Two handmade ceramic bowls side by side, one with deep green matcha and one lighter green matcha, pale wood table, subtle tea leaves, soft warm daylight, cream and sage palette, natural texture, close composition, no text logos labels UI or watermark. Illustrative drinks, not a scientific comparison.

#### powder.png

Use case: photorealistic-natural. Asset type: wide 3:2 editorial photo for a matcha guide. Closeup small wooden spoon piled with fine vivid green matcha powder on ivory linen beside green tea leaves, natural soft morning light, gentle shadows, warm cream and sage palette, understated calm tea ritual, no text labels logos packaging UI or watermark.

#### fields.png

Use case: illustration-story. Asset type: wide landscape image for matcha region guide cards. Soft watercolor illustration of rolling green tea fields, rounded neat tea bushes curving across small hills in gentle morning light, distant hazy mountains, warm cream paper texture and sage green, delicate muted illustration, no identifiable location or buildings, not a photograph of any specific tea region, no text labels logos UI or watermark.
