from django.urls import path
from . import views

app_name = 'highlights'

urlpatterns = [
    path('', views.highlights_gallery, name='gallery'),
]
