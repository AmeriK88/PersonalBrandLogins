from django.db import models

class Highlight(models.Model):
    CATEGORY_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('press', 'Press'),
    ]

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='highlights/images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Video URL")
    press_link = models.URLField(blank=True, null=True, help_text="Link to press article")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"
