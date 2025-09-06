from django.contrib import admin
from .models import Quote, Source

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'get_quote_count']
    list_filter = ['type']
    search_fields = ['name']
    
    def get_quote_count(self, obj):
        return obj.quote_set.count()
    get_quote_count.short_description = 'Количество цитат'

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'source', 'weight', 'views', 'likes', 'dislikes', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['text', 'source__name']
    ordering = ['-created_at']
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст цитаты'