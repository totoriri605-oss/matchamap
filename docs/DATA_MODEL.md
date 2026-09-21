# 말차요정지도 — Data Model Guide

2026-09-20 코드 기준. 실제 정의는 [models.py](../cafeapp/models.py), 입력 검증은 [forms.py](../cafeapp/forms.py)를 참고한다.
미래 설계 후보와 현재 모델을 구분하며, 문서 추가만으로 모델을 변경하지 않는다.

## 1. Cafe — 현재 모델

2026-09-21 다도시 확장: `country`(KR/JP/US, 기본 KR), `city`(seoul/tokyo/osaka/new-york/san-francisco, 기본 seoul)를 추가했다. Admin 모델 검증에서 국가·도시 조합을 검사한다. 기존 `area`와 주소·이미지는 보존한다. migration 0012는 기존 주소/지역에서 확인되는 해외 도시를 분류한다. 도시 이름과 지도 기본 범위는 `cafeapp/locations.py`에서 관리한다.

| 필드 | 형식 및 제약 |
|---|---|
| `name`, `area`, `menu_name` | 문자열, 최대 100자 |
| `address` | 문자열, 최대 255자 |
| `description` | 본문 텍스트 |
| `business_hours` | 최대 200자, 빈 값 허용 |
| `price` | 0 이상 정수 |
| `image` | 이미지, 빈 값 허용, 업로드 경로 `cafes/` |
| `latitude`, `longitude` | 전체 9자리·소수 6자리 Decimal, 미입력 허용 |
| `matcha_strength`, `bitterness`, `sweetness`, `milkiness`, `matcha_aroma` | 1~5 범위 검증기가 있는 정수, 미입력 허용 |
| `is_decaf`, `is_vegan`, `has_parking`, `has_takeout` | Boolean, 기본값 False |
| `is_matchayojung_pick` | 운영자가 직접 추천한 카페 여부, 기본값 False |
| `matchayojung_comment` | 운영자 한줄평, 최대 200자, 빈 값 허용 |
| `blog_url` | 운영자 블로그 후기 URL, 빈 값 허용 |

맛 점수가 없다는 것은 0점이라는 뜻이 아니다. 범위 검증기는 모델 검증과 폼에서 사용하며, 모든 직접 DB 쓰기에 자동으로 적용되는 제약조건으로 가정하지 않는다.
편의 옵션은 현재 True/False만 표현하며 미확인 상태를 별도로 구분하지 않는다.

말차요정 PICK·한줄평·블로그 URL은 Cafe에 직접 저장한다. 한줄평과 URL이 비어 있으면 상세 페이지의 해당 영역을 표시하지 않는다.

`aroma`, `decaf`, `vegan`, `parking`, `takeout`이라는 별도 필드는 없다.

## 2. Review — 현재 모델

- `cafe`: Cafe 외래 키, 역참조 `reviews`.
- `author`: 사용자 외래 키, 역참조 `reviews`.
- `rating`: 1~5 범위 검증기가 있는 정수.
- `comment`: 최대 200자. 폼에서 앞뒤 공백을 제거하고 빈 한줄평을 거절한다.
- `created_at`, `updated_at`: 작성·수정 시각.
- `(cafe, author)`는 DB 유일성 제약으로 사용자당 카페별 1개만 허용한다.
- 기본 조회는 최신 작성순이다. 현재 사용자 기능은 작성·조회·본인 삭제이며 수정 화면은 없다.
- 평균 평점과 리뷰 수는 Review를 집계한다. Cafe에 별도 `rating`, `review_count` 저장 필드를 추가하지 않는다.
- 목록·지도 팝업과 상세 뷰에서 평균과 개수를 계산한다. 리뷰가 없으면 평균은 None, 개수는 0이다.

## 3. Favorite — 현재 모델

- `cafe`, `user`: 카페와 사용자 외래 키.
- `created_at`: 저장 시각.
- `(cafe, user)` DB 유일성 제약으로 중복 저장을 막는다.
- 기존 연결 모델을 재사용한다.

Review와 Favorite은 연결된 카페 또는 사용자가 삭제되면 함께 삭제되는 CASCADE 관계다.

## 4. CafeSuggestion — 현재 모델

- `name`, `area`, `address`, `menu_name`, `price`, `description`.
- `status`: `pending`(기본값), `approved`, `rejected`.
- `created_at`: 제보 시각.
- 로그인 없이 제보할 수 있으며 Cafe와 별도 데이터로 저장한다.

[관리자 코드](../cafeapp/admin.py)에는 세 작업이 있다.

| 작업 | 결과 |
|---|---|
| 승인으로 변경 | 상태만 approved로 변경 |
| 승인하고 Cafe로 등록 | 제보의 여섯 정보로 Cafe를 조회·생성하고 approved로 변경 |
| 거절로 변경 | 상태만 rejected로 변경 |

승인 상태만 저장했다고 Cafe가 자동 생성되지는 않는다.
등록 작업은 여섯 정보가 모두 같은 Cafe를 재사용하며, 카페 이름만으로 중복을 판단하지 않는다.
제보와 생성된 Cafe 사이에 직접 연결 필드는 없다. 이미지·좌표·맛 점수는 제보 폼에서 받지 않으므로 등록 후 별도 보완이 필요하다.

## 5. 향후 설계 후보 — 미구현

- 위치: 기존 `area`를 보존하면서 `country`, `city` 확장을 검토한다.
- 해외 가격: 현지 통화와 소수 단위 가격 정책을 먼저 결정한다.
- 태그: 현재 Tag 모델은 없다. 실제 관리 요구가 생기면 문자열 또는 별도 Tag 관계를 검토한다.
- 맛 표시: `1~2 → 연함/적음`, `3 → 보통`, `4~5 → 진함/많음`은 표시 제안이다. 검색 범위나 임곗값의 확정 규칙이 아니다.

모델 변경 시 필요성, migration 여부, 기존 데이터 영향과 기본값·null 처리를 설명한다.
기존 데이터나 migration 파일을 임의로 삭제하지 않는다.
필터·추천 계산 규칙은 [FEATURES](FEATURES.md)에 둔다.

## Hero 배너 관리 (2026-09-21)

HeroBanner는 사이트 전체에서 한 개만 사용하는 설정이다. 기본 키 1 제약, 선택적 image(업로드 경로 hero/), position(center/left/right, 기본 center)을 가진다. Cafe와 관계가 없으며 이미지 삭제는 설정의 이미지 연결을 제거한다. 기존 업로드 파일을 저장소에서 자동 삭제하지는 않는다.
