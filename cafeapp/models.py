from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from .locations import COUNTRIES, CITIES


class Cafe(models.Model):
    country = models.CharField('국가', max_length=2, choices=list(COUNTRIES.items()), default='KR')
    city = models.CharField('도시', max_length=30, choices=[(key, value['name']) for key, value in CITIES.items()], default='seoul')

    def clean(self):
        super().clean()
        if self.city in CITIES and CITIES[self.city]['country'] != self.country:
            raise ValidationError({'city': '선택한 국가에 속하는 도시를 선택해주세요.'})

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cafes/', blank=True)
    area = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    menu_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    business_hours = models.CharField(max_length=200, blank=True)
    matcha_strength = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    bitterness = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    sweetness = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    milkiness = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    matcha_aroma = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    is_decaf = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_takeout = models.BooleanField(default=False)
    is_matchayojung_pick = models.BooleanField('말차요정 PICK', default=False)
    matchayojung_comment = models.TextField(
        '말차요정 한줄평',
        max_length=200,
        blank=True,
    )
    blog_url = models.URLField('블로그 후기 URL', blank=True)


class Favorite(models.Model):
    cafe = models.ForeignKey(
        Cafe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('cafe', 'user'),
                name='unique_favorite_per_cafe_user',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.cafe.name}'


class CafeSuggestion(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '검토 대기'
        APPROVED = 'approved', '승인'
        REJECTED = 'rejected', '거절'

    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    menu_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    cafe = models.ForeignKey(
        Cafe,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('cafe', 'author'),
                name='unique_review_per_cafe_author',
            ),
        ]

    def __str__(self):
        return f'{self.cafe.name} - {self.author} ({self.rating})'


class HeroBanner(models.Model):
    class Position(models.TextChoices):
        CENTER = 'center', '가운데'
        LEFT = 'left', '왼쪽'
        RIGHT = 'right', '오른쪽'

    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    image = models.ImageField('Hero 대표 이미지', upload_to='hero/', blank=True,
        help_text='가로형 이미지(권장 1600×1000)를 사용하세요. 비어 있으면 기존 일러스트가 표시됩니다.')
    position = models.CharField('이미지 위치', max_length=6, choices=Position.choices, default=Position.CENTER)

    class Meta:
        verbose_name = '메인 Hero 배너'
        verbose_name_plural = '메인 Hero 배너'
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name='single_hero_banner')]

    def __str__(self):
        return '메인 Hero 배너'
