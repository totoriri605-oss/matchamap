from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Cafe(models.Model):
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
