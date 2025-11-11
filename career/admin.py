from django.contrib import admin
from .models import Experience

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('team', 'category', 'country', 'league', 'years')
    list_filter = ('category', 'country')
    search_fields = ('team', 'league', 'country')
