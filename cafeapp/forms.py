from django import forms
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from .locations import CITIES, COUNTRIES
from .models import CafeSuggestion, Review


TASTE_LEVEL_CHOICES = [('', _('선택 안 함'))] + [
    (score, format_lazy(_('{score}점'), score=score)) for score in range(1, 6)
]
TASTE_PREFERENCE_CHOICES = [
    (score, format_lazy(_('{score}점'), score=score)) for score in range(1, 6)
]


class CafeTasteFilterForm(forms.Form):
    matcha_strength = forms.TypedChoiceField(
        label=_('진하기(이상)'),
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    bitterness = forms.TypedChoiceField(
        label=_('쌉싸름함(이상)'),
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    sweetness = forms.TypedChoiceField(
        label=_('단맛(이하)'),
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    milkiness = forms.TypedChoiceField(
        label=_('우유맛(이하)'),
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    matcha_aroma = forms.TypedChoiceField(
        label=_('말차 향(이상)'),
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    is_decaf = forms.BooleanField(label=_('디카페인'), required=False)
    is_vegan = forms.BooleanField(label=_('비건 메뉴'), required=False)
    has_parking = forms.BooleanField(label=_('주차 가능'), required=False)
    has_takeout = forms.BooleanField(label=_('테이크아웃'), required=False)


class CafeRecommendationForm(forms.Form):
    matcha_strength = forms.TypedChoiceField(
        label=_('원하는 진하기'),
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    bitterness = forms.TypedChoiceField(
        label=_('원하는 쌉싸름함'),
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    sweetness = forms.TypedChoiceField(
        label=_('원하는 단맛'),
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    milkiness = forms.TypedChoiceField(
        label=_('원하는 우유맛'),
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    matcha_aroma = forms.TypedChoiceField(
        label=_('원하는 말차 향'),
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    is_decaf = forms.BooleanField(label=_('디카페인 필수'), required=False)
    is_vegan = forms.BooleanField(label=_('비건 메뉴 필수'), required=False)
    has_parking = forms.BooleanField(label=_('주차 필수'), required=False)
    has_takeout = forms.BooleanField(label=_('테이크아웃 필수'), required=False)


def _grouped_city_choices():
    """(국가 이름, [(도시 키, 도시 이름), ...]) 형태로 묶어 드롭다운에 국가별로 보여준다."""
    return [
        (country_name, [(key, city['name']) for key, city in CITIES.items() if city['country'] == code])
        for code, country_name in COUNTRIES.items()
    ]


class CafeSuggestionForm(forms.ModelForm):
    # 국가는 고른 도시에서 정해지므로 입력받지 않는다(어긋난 조합을 막기 위함).
    city = forms.ChoiceField(label=_('도시'), choices=_grouped_city_choices, initial='seoul')

    class Meta:
        model = CafeSuggestion
        fields = (
            'name',
            'city',
            'area',
            'address',
            'menu_name',
            'price',
            'description',
        )
        labels = {
            'name': _('카페 이름'),
            'area': _('지역'),
            'address': _('주소'),
            'menu_name': _('대표 말차 메뉴'),
            'price': _('가격'),
            'description': _('설명'),
        }

    def save(self, commit=True):
        self.instance.country = CITIES[self.cleaned_data['city']]['country']
        return super().save(commit=commit)


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label=_('별점'),
        choices=[(score, format_lazy(_('{score}점'), score=score)) for score in range(5, 0, -1)],
        coerce=int,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        labels = {'comment': _('한줄평')}
        error_messages = {
            'comment': {'required': _('한줄평을 입력해주세요.')},
        }
        widgets = {
            'comment': forms.TextInput(
                attrs={
                    'maxlength': 200,
                    'placeholder': _('이 카페의 말차는 어땠나요?'),
                },
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data['comment'].strip()
        if not comment:
            raise forms.ValidationError(_('한줄평을 입력해주세요.'))
        return comment


class CafeImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV 파일',
        help_text='아래 형식에 맞춰 작성한 .csv 파일을 선택해주세요.',
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.lower().endswith('.csv'):
            raise forms.ValidationError('.csv 파일만 업로드할 수 있습니다.')
        return csv_file
