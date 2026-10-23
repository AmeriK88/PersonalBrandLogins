from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import FamilyPage, FamilyPhoto


class FamilyPhotoInline(TabularInline):
    model = FamilyPhoto
    fields = ('image', 'alt_text', 'caption', 'sort_order', 'is_visible')
    ordering = ('sort_order', 'pk')
    extra = 2


@admin.register(FamilyPage)
class FamilyPageAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    inlines = [FamilyPhotoInline]
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Page Identity', {
            'fields': ('title', 'subtitle'),
        }),
        ('Main Content', {
            'fields': ('introduction', 'family_reflection'),
        }),
        ('Hero Image', {
            'fields': ('hero_image', 'hero_image_alt'),
        }),
        ('Closing Message', {
            'fields': ('closing_quote',),
        }),
        ('Publication', {
            'fields': ('is_published', 'updated_at'),
        }),
    )
    list_display = ('title', 'is_published', 'updated_at')
    list_display_links = ('title',)

    def has_add_permission(self, request):
        return (
            not FamilyPage.objects.exists()
            and super().has_add_permission(request)
        )

    def has_delete_permission(self, request, obj=None):
        return False
