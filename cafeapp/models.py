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
