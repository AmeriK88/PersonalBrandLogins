from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F

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
    years = models.CharField(
        max_length=50,
        help_text="Displayed as entered. Example: 2012–2015.",
    )
    start_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1000), MaxValueValidator(9999)],
        help_text=(
            "First year used for chronological ordering. Enter this manually "
            "when the displayed years are ambiguous or were not imported."
        ),
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark this experience for editorial emphasis.",
    )
    achievements = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='media/', blank=True, null=True)

    class Meta:
        ordering = [F("start_year").asc(nulls_last=True), "pk"]

    def __str__(self):
        return f"{self.team} ({self.years})"


class CareerProfile(models.Model):
    professional_seasons = models.PositiveSmallIntegerField(
        default=13, help_text="Supplied career total shown on the Career page."
    )
    countries = models.PositiveSmallIntegerField(
        default=9, help_text="Supplied career total shown on the Career page."
    )
    teams = models.PositiveSmallIntegerField(
        default=15, help_text="Supplied career total shown on the Career page."
    )
    games = models.PositiveIntegerField(default=390)
    minutes = models.PositiveIntegerField(default=9750)
    points = models.PositiveIntegerField(default=5070)
    rebounds = models.PositiveIntegerField(default=2340)
    assists = models.PositiveIntegerField(default=1170)
    steals = models.PositiveIntegerField(default=390)

    full_name = models.CharField(max_length=150, default="Gregory Mark Logins Jr.")
    birth_date = models.DateField(default=date(1988, 3, 16))
    birthplace = models.CharField(
        max_length=150, default="Sodus, New York, USA"
    )
    college = models.CharField(max_length=150, default="Canisius College")
    college_years = models.CharField(max_length=50, default="2007–2011")
    degrees = models.CharField(
        max_length=255,
        default="BSc Physical Education & Health · Master’s in Sports Administration",
    )
    known_for = models.CharField(
        max_length=255, default="Leadership · Versatility · Comebacks"
    )
    current_role = models.CharField(
        max_length=255, default="Education TA · Father · Mentor"
    )

    class Meta:
        verbose_name = "Career profile and statistics"
        verbose_name_plural = "Career profile and statistics"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Career profile and statistics"
