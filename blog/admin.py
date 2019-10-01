from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date')
    list_filter = ('created_date', 'published_date', 'author')
    search_fields = ('title', 'text')
    date_hierarchy = 'published_date'
    ordering = ('published_date', )
    raw_id_fields = ('author',)


admin.site.register(Comment)
