from django.db import models

class Experience(models.Model):
    CATEGORY_CHOICES = [
        ('high_school', 'High School'),
        ('college', 'College'),
        ('professional', 'Professional'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    country = models.CharField(max_length=100, blank=True, null=True)
    team = models.CharField(max_length=100)
    league = models.CharField(max_length=100, blank=True, null=True)
    years = models.CharField(max_length=50, help_text="Example: 2012–2015")
    achievements = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='media/', blank=True, null=True)

    class Meta:
        ordering = ['-years']

    def __str__(self):
        return f"{self.team} ({self.years})"
