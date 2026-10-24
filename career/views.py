from django.shortcuts import render
from .models import CareerProfile, Experience

def career_overview(request):
    experiences = list(Experience.objects.all())
    profile = CareerProfile.objects.filter(pk=1).first() or CareerProfile(pk=1)
    grouped_experiences = {
        category: [experience for experience in experiences if experience.category == category]
        for category in ("high_school", "college", "professional")
    }

    context = {
        **grouped_experiences,
        "profile": profile,
        "headline_stats": (
            (profile.professional_seasons, "Professional seasons"),
            (profile.countries, "Countries"),
            (profile.teams, "Teams"),
        ),
        "performance_stats": (
            (f"{profile.games:,}", "Games"),
            (f"{profile.minutes:,}", "Minutes"),
            (f"{profile.points:,}", "Points"),
            (f"{profile.rebounds:,}", "Rebounds"),
            (f"{profile.assists:,}", "Assists"),
            (f"{profile.steals:,}", "Steals"),
        ),
    }
    return render(request, 'career/overview.html', context)
