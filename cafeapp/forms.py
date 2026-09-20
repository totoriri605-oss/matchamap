from django import forms

from .models import CafeSuggestion, Review


TASTE_LEVEL_CHOICES = [('', '선택 안 함')] + [
    (score, f'{score}점') for score in range(1, 6)
]
TASTE_PREFERENCE_CHOICES = [
    (score, f'{score}점') for score in range(1, 6)
]


class CafeTasteFilterForm(forms.Form):
    matcha_strength = forms.TypedChoiceField(
        label='진하기(이상)',
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    bitterness = forms.TypedChoiceField(
        label='쌉싸름함(이상)',
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    sweetness = forms.TypedChoiceField(
        label='단맛(이하)',
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    milkiness = forms.TypedChoiceField(
        label='우유맛(이하)',
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    matcha_aroma = forms.TypedChoiceField(
        label='말차 향(이상)',
        choices=TASTE_LEVEL_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
    )
    is_decaf = forms.BooleanField(label='디카페인', required=False)
    is_vegan = forms.BooleanField(label='비건 메뉴', required=False)
    has_parking = forms.BooleanField(label='주차 가능', required=False)
    has_takeout = forms.BooleanField(label='테이크아웃', required=False)


class CafeRecommendationForm(forms.Form):
    matcha_strength = forms.TypedChoiceField(
        label='원하는 진하기',
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    bitterness = forms.TypedChoiceField(
        label='원하는 쌉싸름함',
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    sweetness = forms.TypedChoiceField(
        label='원하는 단맛',
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    milkiness = forms.TypedChoiceField(
        label='원하는 우유맛',
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    matcha_aroma = forms.TypedChoiceField(
        label='원하는 말차 향',
        choices=TASTE_PREFERENCE_CHOICES,
        coerce=int,
    )
    is_decaf = forms.BooleanField(label='디카페인 필수', required=False)
    is_vegan = forms.BooleanField(label='비건 메뉴 필수', required=False)
    has_parking = forms.BooleanField(label='주차 필수', required=False)
    has_takeout = forms.BooleanField(label='테이크아웃 필수', required=False)


class CafeSuggestionForm(forms.ModelForm):
    class Meta:
        model = CafeSuggestion
        fields = (
            'name',
            'area',
            'address',
            'menu_name',
            'price',
            'description',
        )
        labels = {
            'name': '카페 이름',
            'area': '지역',
            'address': '주소',
            'menu_name': '대표 말차 메뉴',
            'price': '가격',
            'description': '설명',
        }


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label='별점',
        choices=[(score, f'{score}점') for score in range(5, 0, -1)],
        coerce=int,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        labels = {'comment': '한줄평'}
        error_messages = {
            'comment': {'required': '한줄평을 입력해주세요.'},
        }
        widgets = {
            'comment': forms.TextInput(
                attrs={
                    'maxlength': 200,
                    'placeholder': '이 카페의 말차는 어땠나요?',
                },
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data['comment'].strip()
        if not comment:
            raise forms.ValidationError('한줄평을 입력해주세요.')
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
