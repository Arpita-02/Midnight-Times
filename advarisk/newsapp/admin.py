from django.contrib import admin
from .models import Keyword,Article
# Register your models here.
class KeywordAdmin(admin.ModelAdmin):
    list_display=['user','keyword','last_searched','latest_published_at']

admin.site.register(Keyword, KeywordAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display=['keyword','articles_list']

admin.site.register(Article, ArticleAdmin)
