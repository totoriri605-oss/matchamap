from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Cafe, CafeSuggestion, Favorite, Review, HeroBanner


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
