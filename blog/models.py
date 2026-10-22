from django.db import models
from django.utils.text import slugify
from django.urls import reverse 
from django.core.exceptions import ValidationError

from .storage import BlogMediaStorage
from .validators import validate_audio_upload, validate_video_upload

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('mindset', 'Mindset'),
        ('training', 'Training'),
        ('student_athlete', 'Student-Athlete'),
        ('parents', 'For Parents'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    excerpt = models.TextField(blank=True, null=True, help_text="Short intro for lists and previews.")
    content = models.TextField()
    cover_image = models.ImageField(upload_to='blog/covers/', blank=True, null=True)
    narration_audio = models.FileField(
        upload_to='blog/narration/',
        storage=BlogMediaStorage('video'),
        validators=[validate_audio_upload],
        blank=True,
    )
    reel_title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Optional title displayed above the article reel.",
    )
    reel_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional short description displayed below the reel title.",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])


class PostReelMedia(models.Model):
    IMAGE = 'image'
    VIDEO = 'video'
    MEDIA_TYPE_CHOICES = [
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    post = models.ForeignKey(Post, related_name='reel_media', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES)
    image = models.ImageField(
        upload_to='blog/reels/images/',
        storage=BlogMediaStorage('image'),
        blank=True,
    )
    video = models.FileField(
        upload_to='blog/reels/videos/',
        storage=BlogMediaStorage('video'),
        validators=[validate_video_upload],
        blank=True,
    )
    order = models.PositiveIntegerField(default=0)
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.get_media_type_display()} for {self.post}'

    def clean(self):
        super().clean()
        errors = {}
        if not self.image and not self.video:
            errors['image'] = 'Upload a file for this reel item.'
        if self.media_type == self.IMAGE and self.video:
            errors['video'] = 'Select an image reel item or a video reel item, not both.'
        elif self.media_type == self.VIDEO and self.image:
            errors['image'] = 'Select a video reel item or an image reel item, not both.'
        if self.image and self.video:
            errors['image'] = 'A reel item can contain only one media file.'
            errors['video'] = 'A reel item can contain only one media file.'
        if errors:
            raise ValidationError(errors)
