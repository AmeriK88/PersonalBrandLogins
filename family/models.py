from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.deconstruct import deconstructible

from .validators import validate_no_gps_metadata


@deconstructible
class FamilyImageUploadTo:
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, _instance, filename):
        extension = Path(filename).suffix.lower()
        return f'family/{self.folder}/{uuid4().hex}{extension}'


class FamilyPage(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )
    title = models.CharField(max_length=150, default='Family First')
    subtitle = models.CharField(max_length=255, blank=True)
    introduction = models.TextField(blank=True)
    family_reflection = models.TextField(blank=True)
    hero_image = models.ImageField(
        upload_to=FamilyImageUploadTo('hero'),
        validators=[validate_no_gps_metadata],
        blank=True,
        help_text='Use an approved public photo with GPS metadata removed.',
    )
    hero_image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text='Required when a hero image is uploaded.',
    )
    closing_quote = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name='family_page_singleton_id',
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.hero_image and not self.hero_image_alt.strip():
            raise ValidationError({
                'hero_image_alt': 'Provide alternative text for the hero image.'
            })


class FamilyPhoto(models.Model):
    page = models.ForeignKey(
        FamilyPage,
        related_name='photos',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to=FamilyImageUploadTo('gallery'),
        validators=[validate_no_gps_metadata],
        help_text='Use an approved public photo with GPS metadata removed.',
    )
    alt_text = models.CharField(max_length=255)
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'pk']

    def __str__(self):
        return self.caption or f'Family photo {self.pk}'
