from django.contrib import admin
from .models import InvestmentInstrument, MarketEvent, GameSession, Investment, GameTurn

@admin.register(InvestmentInstrument)
class InvestmentInstrumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'instrument_type', 'base_return', 'risk_level']
    list_filter = ['instrument_type', 'risk_level']
    search_fields = ['name']

@admin.register(MarketEvent)
class MarketEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'return_modifier']
    list_filter = ['event_type']
    filter_horizontal = ['affected_instruments']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_week', 'current_capital', 'is_finished', 'created_at']
    list_filter = ['is_finished', 'created_at']
    readonly_fields = ['created_at', 'finished_at']

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'instrument', 'amount']
    list_filter = ['instrument']

@admin.register(GameTurn)
class GameTurnAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'week_number', 'event', 'capital_before', 'capital_after', 'created_at']
    list_filter = ['week_number', 'created_at']
    readonly_fields = ['created_at']