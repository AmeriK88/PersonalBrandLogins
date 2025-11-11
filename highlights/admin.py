from django.contrib import admin
from .models import Highlight

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
