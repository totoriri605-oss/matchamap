from django.contrib import admin

from .models import Cafe, CafeSuggestion, Favorite, Review


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
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
        (
            '기본 정보',
            {
                'fields': (
                    'name',
                    'image',
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
