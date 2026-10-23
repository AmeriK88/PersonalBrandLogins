from django.shortcuts import get_object_or_404, render

from .models import FamilyPage, FamilyPhoto


def overview(request):
    page = get_object_or_404(
        FamilyPage.objects.prefetch_related('photos'),
        is_published=True,
    )
    photos = FamilyPhoto.objects.filter(
        page=page,
        is_visible=True,
    ).exclude(image='')
    return render(
        request,
        'family/overview.html',
        {
            'page': page,
            'photos': photos,
        },
    )
