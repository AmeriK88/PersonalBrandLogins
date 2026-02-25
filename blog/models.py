from django.db import models
from django.utils.text import slugify
from django.urls import reverse 

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
