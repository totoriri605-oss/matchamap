import csv
import io
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from .forms import CafeImportForm
from .models import Cafe, CafeSuggestion, Favorite, Review, HeroBanner

CAFE_IMPORT_INT_FIELDS = (
    'matcha_strength',
    'bitterness',
    'sweetness',
    'milkiness',
    'matcha_aroma',
)
CAFE_IMPORT_BOOLEAN_FIELDS = (
    'is_decaf',
    'is_vegan',
    'has_parking',
    'has_takeout',
)
CAFE_IMPORT_TRUE_VALUES = {'1', 'true', 'yes', 'y', 'o', '참'}


class CafeAdminForm(forms.ModelForm):
    class Meta:
        model = Cafe
        fields = '__all__'
        labels = {'image': '대표 사진'}
        help_texts = {
            'image': '사진을 선택하고 저장하면 메인 카드와 상세 페이지에 반영됩니다. 교체하려면 새 파일을 선택하고, 제거하려면 현재 파일의 지우기를 선택하세요.',
        }
        widgets = {'image': forms.ClearableFileInput(attrs={'accept': 'image/*'})}


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    form = CafeAdminForm
    readonly_fields = ('image_preview',)
    change_list_template = 'admin/cafeapp/cafe_change_list.html'

    def get_urls(self):
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv),
                name='cafeapp_cafe_import_csv',
            ),
        ]
        return custom_urls + super().get_urls()

    def import_csv(self, request):
        if request.method == 'POST':
            form = CafeImportForm(request.POST, request.FILES)
            if form.is_valid():
                created_count, updated_count, error_rows = self._import_cafes_from_csv(
                    request.FILES['csv_file'],
                )
                if created_count or updated_count:
                    messages.success(
                        request,
                        f'{created_count}개 카페를 새로 등록하고, {updated_count}개를 갱신했습니다.',
                    )
                if error_rows:
                    messages.warning(
                        request,
                        '다음 행은 건너뛰었습니다: ' + ' / '.join(error_rows[:10]),
                    )
                if not created_count and not updated_count and not error_rows:
                    messages.warning(request, '처리할 데이터가 없습니다. 파일 내용을 확인해주세요.')
                return redirect('admin:cafeapp_cafe_changelist')
        else:
            form = CafeImportForm()

        return render(
            request,
            'admin/cafeapp/cafe_import_csv.html',
            {
                'form': form,
                'opts': self.model._meta,
                'title': 'CSV로 카페 일괄 등록',
            },
        )

    def _import_cafes_from_csv(self, uploaded_file):
        decoded = io.TextIOWrapper(uploaded_file.file, encoding='utf-8-sig')
        reader = csv.DictReader(decoded)

        created_count = 0
        updated_count = 0
        error_rows = []

        for row_number, row in enumerate(reader, start=2):
            name = (row.get('name') or '').strip()
            area = (row.get('area') or '').strip()
            if not name or not area:
                continue

            try:
                defaults = {
                    'address': (row.get('address') or '').strip(),
                    'menu_name': (row.get('menu_name') or '').strip(),
                    'price': int((row.get('price') or '0').strip() or 0),
                    'description': (row.get('description') or '').strip(),
                    'business_hours': (row.get('business_hours') or '').strip(),
                }

                for field_name in CAFE_IMPORT_INT_FIELDS:
                    value = (row.get(field_name) or '').strip()
                    defaults[field_name] = int(value) if value else None

                for field_name in CAFE_IMPORT_BOOLEAN_FIELDS:
                    value = (row.get(field_name) or '').strip().lower()
                    defaults[field_name] = value in CAFE_IMPORT_TRUE_VALUES

                latitude = (row.get('latitude') or '').strip()
                longitude = (row.get('longitude') or '').strip()
                defaults['latitude'] = Decimal(latitude) if latitude else None
                defaults['longitude'] = Decimal(longitude) if longitude else None

                cafe = Cafe(name=name, area=area, **defaults)
                cafe.full_clean(exclude=['image'])

                _, created = Cafe.objects.update_or_create(
                    name=name,
                    area=area,
                    defaults=defaults,
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except (ValueError, InvalidOperation) as exc:
                error_rows.append(f'{row_number}행: 값을 읽을 수 없습니다 ({exc})')
            except ValidationError as exc:
                error_rows.append(f'{row_number}행: {"; ".join(exc.messages)}')

        return created_count, updated_count, error_rows

    @admin.display(description='대표 사진')
    def image_thumbnail(self, obj):
        if not obj.image:
            return '사진 없음'
        return format_html('<img src="{}" alt="{}" width="72" height="54" style="object-fit:cover;border-radius:6px">', obj.image.url, obj.name)

    @admin.display(description='현재 사진')
    def image_preview(self, obj):
        if not obj or not obj.image:
            return '등록된 사진이 없습니다. 아래에서 대표 사진을 선택해주세요.'
        return format_html('<img src="{}" alt="{}" style="max-width:360px;width:100%;max-height:260px;object-fit:contain;border-radius:8px">', obj.image.url, obj.name)

    list_display = (
        'name',
        'image_thumbnail',
        'area',
        'matcha_strength',
        'sweetness',
        'is_decaf',
        'is_vegan',
        'has_parking',
        'has_takeout',
    )
    list_filter = (
        'area',
        'is_decaf',
        'is_vegan',
        'has_parking',
        'has_takeout',
    )
    search_fields = ('name', 'area', 'address', 'menu_name')
    fieldsets = (
        ('대표 사진', {'fields': ('image_preview', 'image')}),
        (
            '기본 정보',
            {
                'fields': (
                    'name',
                    'area',
                    'address',
                    ('latitude', 'longitude'),
                    'business_hours',
                    'menu_name',
                    'price',
                    'description',
                ),
            },
        ),
        (
            '말차 맛 특성',
            {
                'fields': (
                    'matcha_strength',
                    'bitterness',
                    'sweetness',
                    'milkiness',
                    'matcha_aroma',
                ),
                'description': '각 항목을 1점부터 5점 사이로 입력하세요.',
            },
        ),
        (
            '편의 정보',
            {
                'fields': (
                    'is_decaf',
                    'is_vegan',
                    'has_parking',
                    'has_takeout',
                ),
            },
        ),
    )


@admin.register(CafeSuggestion)
class CafeSuggestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'status', 'created_at')
    list_filter = ('status',)
    actions = (
        'approve_and_create_cafes',
        'approve_suggestions',
        'reject_suggestions',
    )

    @admin.action(description='선택한 제보를 승인하고 Cafe로 등록')
    def approve_and_create_cafes(self, request, queryset):
        created_count = 0

        for suggestion in queryset:
            _, created = Cafe.objects.get_or_create(
                name=suggestion.name,
                area=suggestion.area,
                address=suggestion.address,
                menu_name=suggestion.menu_name,
                price=suggestion.price,
                description=suggestion.description,
            )
            if created:
                created_count += 1

        queryset.update(status=CafeSuggestion.Status.APPROVED)
        self.message_user(
            request,
            f'{created_count}개의 카페를 등록했습니다. 이미 등록된 동일 카페는 건너뛰었습니다.',
        )

    @admin.action(description='선택한 제보를 승인으로 변경')
    def approve_suggestions(self, request, queryset):
        queryset.update(status=CafeSuggestion.Status.APPROVED)

    @admin.action(description='선택한 제보를 거절로 변경')
    def reject_suggestions(self, request, queryset):
        queryset.update(status=CafeSuggestion.Status.REJECTED)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('cafe', 'author', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('cafe__name', 'author__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'cafe', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'cafe__name')


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    fields = ('image_preview', 'image', 'position')
    readonly_fields = ('image_preview',)
    list_display = ('__str__', 'image_preview', 'position')

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not HeroBanner.objects.exists()

    @admin.display(description='이미지 미리보기')
    def image_preview(self, obj):
        if not obj or not obj.image:
            return '이미지가 없습니다. 기본 말차 일러스트를 사용합니다.'
        return format_html(
            '<img src="{}" alt="Hero 미리보기" style="width:100%;max-width:400px;aspect-ratio:8/5;object-fit:cover;object-position:{};border-radius:12px">',
            obj.image.url, obj.position,
        )
