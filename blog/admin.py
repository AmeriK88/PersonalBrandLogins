from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter
from unfold.decorators import action
from unfold.enums import ActionVariant

from .models import Post


@admin.register(Post)
class PostAdmin(ModelAdmin):
    # Options UX Unfold
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True
    list_filter_submit = True

    list_display = (
        "title",
        "category_badge",
        "status_badge",
        "cover_thumb",
        "created_at",
        "updated_at",
    )
    list_display_links = ("title",)

    # FILTERS
    search_fields = ("title", "content", "excerpt")
    list_filter = [
        ("title", FieldTextFilter),
        "category",
        "is_published",
        ("created_at", RangeDateTimeFilter),
        ("updated_at", RangeDateTimeFilter),
    ]

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25

    prepopulated_fields = {"slug": ("title",)}

    # BULK ACTIONS
    actions = ["publish_posts", "unpublish_posts", "clear_cover_image"]

    @action(
        description="Mark as published",
        icon="check_circle",
        variant=ActionVariant.SUCCESS,
    )
    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Marked {updated} post(s) as published.")

    @action(
        description="Mark as draft",
        icon="cancel",
        variant=ActionVariant.INFO,
    )
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Marked {updated} post(s) as draft.")

    @action(
        description="Remove cover image",
        icon="image_not_supported",
        variant=ActionVariant.WARNING,
    )
    def clear_cover_image(self, request, queryset):
        cleared = 0
        for post in queryset:
            if post.cover_image:
                post.cover_image.delete(save=False)
                post.cover_image = None
                post.save(update_fields=["cover_image"])
                cleared += 1
        self.message_user(
            request,
            f"Removed cover image from {cleared} post(s).",
        )

    # === FIELDS ===

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                "<img src='{}' alt='{}' class='admin-thumb admin-thumb-image' />",
                obj.cover_image.url,
                obj.title,
            )
        return "-"

    @admin.display(description="Category")
    def category_badge(self, obj):
        # Use category to customize
        return format_html(
            "<span class='admin-badge admin-badge-post-category admin-badge-post-category-{}'>{}</span>",
            obj.category,
            obj.get_category_display(),
        )

    @admin.display(description="Status")
    def status_badge(self, obj):
        status_class = "admin-badge-status-published" if obj.is_published else "admin-badge-status-draft"
        label = "Published" if obj.is_published else "Draft"
        return format_html(
            "<span class='admin-badge admin-badge-status {}'>{}</span>",
            status_class,
            label,
        )
