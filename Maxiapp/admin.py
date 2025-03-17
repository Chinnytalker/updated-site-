from django.contrib import admin
from .models import Post, Category, Comment, NewsArticle, UserProfile


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "date_created", "image", "updated_by", "views")


class CategoryAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "comment")




admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_name', 'published_at')
    search_fields = ('title', 'source_name')
    list_filter = ('source_name', 'published_at')





