from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter
from unfold.decorators import action
from unfold.enums import ActionVariant

from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(ModelAdmin):
    # UX de Unfold
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True
    list_filter_submit = True

    # Qué se muestra en la lista
    list_display = (
        "team",
        "category_badge",
        "country",
        "league",
        "years",
        "achievements_preview",
        "image_thumb",
    )
    list_display_links = ("team",)

    # Búsqueda y filtros
    search_fields = ("team", "league", "country", "achievements")
    list_filter = [
        ("team", FieldTextFilter),
        "category",
        "country",
    ]

    ordering = ("-years",)   # coherente con el Meta del modelo
    list_per_page = 25

    # Acciones bulk
    actions = ["clear_image"]

    @action(
        description="Remove experience image",
        icon="image_not_supported",
        variant=ActionVariant.WARNING,
    )
    def clear_image(self, request, queryset):
        cleared = 0
        for exp in queryset:
            if exp.image:
                exp.image.delete(save=False)
                exp.image = None
                exp.save(update_fields=["image"])
                cleared += 1
        self.message_user(
            request,
            f"Removed image from {cleared} experience(s).",
        )

    # ==== Campos "bonitos" ====

    @admin.display(description="Category")
    def category_badge(self, obj):
        label = obj.get_category_display()
        # usamos el value de category para construir la clase:
        # high_school / college / professional
        return format_html(
            "<span class='admin-badge admin-badge-exp admin-badge-exp-{}'>{}</span>",
            obj.category,
            label,
        )

    @admin.display(description="Achievements")
    def achievements_preview(self, obj):
        if not obj.achievements:
            return "-"
        text = obj.achievements.strip()
        if len(text) > 60:
            text = text[:57].rstrip() + "..."
        return text

    @admin.display(description="Image")
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' alt='{}' class='admin-thumb admin-thumb-image' />",
                obj.image.url,
                obj.team,
            )
        return "-"
