from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)