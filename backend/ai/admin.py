from django.contrib import admin
from .models import AgentInteractionLog

@admin.register(AgentInteractionLog)
class AgentInteractionLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at')
    list_filter = ('student', 'created_at')
    search_fields = ('student__email', 'user_message', 'agent_response')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'