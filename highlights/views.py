from django.shortcuts import render
from .models import Highlight

def highlights_gallery(request):
    photos = Highlight.objects.filter(category='photo')
    videos = Highlight.objects.filter(category='video')
    press = Highlight.objects.filter(category='press')

    context = {
        'photos': photos,
        'videos': videos,
        'press': press,
    }
    return render(request, 'highlights/gallery.html', context)
