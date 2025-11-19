from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class InvestmentInstrument(models.Model):
    INSTRUMENT_TYPES = [
        ('deposit', 'Банковский вклад'),
        ('stocks', 'Акции'),
        ('bonds', 'Облигации'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название')
    instrument_type = models.CharField(max_length=20, choices=INSTRUMENT_TYPES, verbose_name='Тип инструмента')
    base_return = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Базовая доходность (%)')
    risk_level = models.IntegerField(choices=[(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')], verbose_name='Уровень риска')
    description = models.TextField(verbose_name='Описание')
    
    def __str__(self):
        return f"{self.name} ({self.get_instrument_type_display()})"

class MarketEvent(models.Model):
    EVENT_TYPES = [
        ('positive', 'Положительное'),
        ('negative', 'Отрицательное'),
        ('neutral', 'Нейтральное'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название события')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='Тип события')
    description = models.TextField(verbose_name='Описание')
    affected_instruments = models.ManyToManyField(InvestmentInstrument, verbose_name='Затронутые инструменты')
    return_modifier = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Модификатор доходности (%)')
    
    def __str__(self):
        return self.name

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    current_week = models.IntegerField(default=1, verbose_name='Текущая неделя')
    total_weeks = models.IntegerField(default=12, verbose_name='Всего недель')
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, default=10000, verbose_name='Начальный капитал')
    current_capital = models.DecimalField(max_digits=12, decimal_places=2, default=10000, verbose_name='Текущий капитал')
    is_finished = models.BooleanField(default=False, verbose_name='Завершена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершена')
    
    def get_available_capital(self):
        invested = sum(investment.amount for investment in self.investments.all())
        return self.current_capital - invested
    
    def __str__(self):
        return f"Игра {self.user.username} - Неделя {self.current_week}"

class Investment(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='investments')
    instrument = models.ForeignKey(InvestmentInstrument, on_delete=models.CASCADE, verbose_name='Инструмент')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма инвестиции')
    
    def __str__(self):
        return f"{self.instrument.name}: {self.amount}₽"

class GameTurn(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='turns')
    week_number = models.IntegerField(verbose_name='Номер недели')
    event = models.ForeignKey(MarketEvent, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Событие')
    capital_before = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Капитал до')
    capital_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Капитал после')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    def profit_loss(self):
        return self.capital_after - self.capital_before
    
    def __str__(self):
        return f"Ход {self.week_number} - {self.game_session.user.username}"