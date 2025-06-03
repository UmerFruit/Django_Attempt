from django.contrib import admin
from .models import Whiteboard, WhiteboardSession


@admin.register(Whiteboard)
class WhiteboardAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at', 'updated_at']
    search_fields = ['title', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'owner', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(WhiteboardSession)
class WhiteboardSessionAdmin(admin.ModelAdmin):
    list_display = ['whiteboard', 'user', 'started_at', 'ended_at']
    list_filter = ['started_at', 'ended_at']
    search_fields = ['whiteboard__title', 'user__username']
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'
