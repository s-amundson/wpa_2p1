from django.contrib import admin
from .models import Article, ArticlePage, Category, Faq


@admin.register(Article)
class ArticlePageAdmin(admin.ModelAdmin):
    # list_display = ('id', 'page', 'position', 'status')
    pass

@admin.register(ArticlePage)
class ArticlePageAdmin(admin.ModelAdmin):
    list_display = ('id', 'page')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content',)

