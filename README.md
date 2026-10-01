# 말차요정지도 (matchamap)

말차 카페를 지도에서 찾고, 내 입맛(진하기·쌉싸름함·단맛·우유감·향)에 맞는 카페를 고르는 Django 웹사이트입니다.
서울·도쿄·오사카·뉴욕 등 여러 도시를 지원하고, 한국어/영어 전환, 즐겨찾기, 리뷰, 카페 제보 기능이 있습니다.

## 처음 실행하기 (Windows PowerShell)

```powershell
# 1. 가상환경 만들기 (처음 한 번)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. 라이브러리 설치
pip install -r requirements.txt

# 3. 환경 설정 파일 만들기
copy .env.example .env
#    .env를 열어 SECRET_KEY를 긴 무작위 문자열로 바꾼다.
#    아래 명령으로 만들 수 있다.
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"

# 4. 데이터베이스 만들고 카페 38곳 채우기
python manage.py migrate
python manage.py loaddata seed_cafes

# 5. 관리자 계정 만들기
python manage.py createsuperuser

# 6. 서버 실행
python manage.py runserver
```

브라우저에서 http://127.0.0.1:8000 (사이트), http://127.0.0.1:8000/admin/ (관리자)를 엽니다.
다음부터는 `.venv\Scripts\Activate.ps1`과 `python manage.py runserver`만 하면 됩니다.

## 자주 쓰는 명령

| 하는 일 | 명령 |
|---|---|
| 테스트 실행 | `python manage.py test` |
| DB 구조 변경 반영 | `python manage.py migrate` |
| 관리자 비밀번호 변경 | `python manage.py changepassword 계정이름` |

## 폴더 안내

| 폴더/파일 | 역할 |
|---|---|
| `config/` | 사이트 전체 설정, 주소 연결 |
| `cafeapp/` | 핵심 기능 (모델, 화면, 템플릿, 관리자, 테스트) |
| `cafeapp/fixtures/seed_cafes.json` | 카페 38곳 시드 데이터 |
| `media/` | 업로드된 카페 사진, 배너 |
| `locale/` | 영어 번역 |
| `docs/` | 기능·데이터 구조·규칙 문서 (`docs/README.md`부터 읽기) |

## 주의

- `.env`와 `db.sqlite3`는 git에 올리지 않습니다. 비밀 값과 실제 데이터가 들어 있습니다.
- 구글/카카오 로그인은 각 개발자 콘솔에서 키를 발급받아 관리자 화면(소셜 애플리케이션)에 등록해야 동작합니다.
- 맛 점수는 대부분 아직 비어 있습니다. 자세한 내용은 `docs/TASTE_AUDIT_2026-09-23.md`를 참고하세요.
