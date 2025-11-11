from django.shortcuts import render
from .models import Experience

def career_overview(request):
    high_school = Experience.objects.filter(category='high_school')
    college = Experience.objects.filter(category='college')
    professional = Experience.objects.filter(category='professional')

    context = {
        'high_school': high_school,
        'college': college,
        'professional': professional,
    }
    return render(request, 'career/overview.html', context)
