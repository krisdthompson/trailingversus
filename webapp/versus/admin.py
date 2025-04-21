from django.contrib import admin
from .models import Verse, VerseLine

class VerseLineInline(admin.TabularInline):
    model = VerseLine
    extra = 1
    fields = ('position', 'content', 'grade', 'syllable_count', 'is_syllable_override')
    ordering = ('position',)
    readonly_fields = ('syllable_count',)

@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VerseLineInline]
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('lines')

@admin.register(VerseLine)
class VerseLineAdmin(admin.ModelAdmin):
    list_display = ('verse', 'position', 'content_preview', 'grade', 'syllable_count', 'is_syllable_override')
    list_filter = ('is_syllable_override', 'grade')
    search_fields = ('content', 'verse__title')
    readonly_fields = ('syllable_count',)
    ordering = ('verse', 'position')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
