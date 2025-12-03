from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter
from unfold.decorators import action
from unfold.enums import ActionVariant

from .models import Highlight


@admin.register(Highlight)
class HighlightAdmin(ModelAdmin):
    # UX de Unfold
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True
    list_filter_submit = True

    # Qué se muestra en la lista
    list_display = (
        "title",
        "category_badge",
        "description_preview",
        "image_thumb",
        "video_badge",
        "press_badge",
        "created_at",
    )
    list_display_links = ("title",)

    # Búsqueda y filtros
    search_fields = ("title", "description")
    list_filter = [
        ("title", FieldTextFilter),
        "category",
        ("created_at", RangeDateTimeFilter),
    ]

    ordering = ("-created_at",)
    list_per_page = 25

    # Acciones bulk
    actions = ["clear_image", "clear_links"]

    @action(
        description="Remove image",
        icon="image_not_supported",
        variant=ActionVariant.WARNING,
    )
    def clear_image(self, request, queryset):
        cleared = 0
        for h in queryset:
            if h.image:
                h.image.delete(save=False)
                h.image = None
                h.save(update_fields=["image"])
                cleared += 1
        self.message_user(request, f"Removed image from {cleared} highlight(s).")

    @action(
        description="Clear video & press links",
        icon="link_off",
        variant=ActionVariant.INFO,
    )
    def clear_links(self, request, queryset):
        cleared = 0
        for h in queryset:
            changed = False
            if h.video_url:
                h.video_url = ""
                changed = True
            if h.press_link:
                h.press_link = ""
                changed = True
            if changed:
                h.save(update_fields=["video_url", "press_link"])
                cleared += 1
        self.message_user(request, f"Cleared links from {cleared} highlight(s).")

    # ===== Campos "bonitos" =====

    @admin.display(description="Category")
    def category_badge(self, obj):
        label = obj.get_category_display()
        # usamos la categoría como parte de la clase (photo/video/press)
        return format_html(
            "<span class='admin-badge admin-badge-category admin-badge-category-{}'>{}</span>",
            obj.category,
            label,
        )

    @admin.display(description="Description")
    def description_preview(self, obj):
        if not obj.description:
            return "-"
        text = obj.description.strip()
        if len(text) > 60:
            text = text[:57].rstrip() + "..."
        return text

    @admin.display(description="Image")
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' alt='{}' class='admin-thumb admin-thumb-image' />",
                obj.image.url,
                obj.title,
            )
        return "-"

    @admin.display(description="Video")
    def video_badge(self, obj):
        if not obj.video_url:
            return "-"
        return format_html(
            "<a href='{url}' target='_blank' "
            "class='admin-pill admin-pill-video'>"
            "Video ↗"
            "</a>",
            url=obj.video_url,
        )

    @admin.display(description="Press")
    def press_badge(self, obj):
        if not obj.press_link:
            return "-"
        return format_html(
            "<a href='{url}' target='_blank' "
            "class='admin-pill admin-pill-press'>"
            "Press ↗"
            "</a>",
            url=obj.press_link,
        )
