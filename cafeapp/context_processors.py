from allauth.socialaccount.adapter import get_adapter
from django.utils.functional import SimpleLazyObject

SOCIAL_PROVIDERS = ('google', 'kakao')


def social_login(request):
    """키(SocialApp)가 등록된 소셜 로그인 제공자만 True로 알려준다.

    등록되지 않은 제공자의 로그인 주소를 열면 서버 오류(500)가 나므로,
    템플릿에서 이 값을 보고 버튼을 켤지 '준비 중'으로 보여줄지 정한다.
    값은 템플릿에서 실제로 쓸 때만 계산한다(lazy).
    """
    def configured():
        adapter = get_adapter()
        return {
            provider: bool(adapter.list_apps(request, provider=provider))
            for provider in SOCIAL_PROVIDERS
        }

    return {'social_login': SimpleLazyObject(configured)}
