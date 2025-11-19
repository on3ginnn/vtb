import random
from decimal import Decimal
from .models import MarketEvent, InvestmentInstrument

def calculate_weekly_returns(game_session):
    """Рассчитывает доходность за неделю с учетом случайных событий"""
    
    # Получаем случайное событие (с шансом 70%)
    event = None
    if random.random() < 0.7:
        events = list(MarketEvent.objects.all())
        if events:
            event = random.choice(events)
    
    capital_before = game_session.current_capital
    total_return = Decimal('0')
    
    # Рассчитываем доходность по каждой инвестиции
    for investment in game_session.investments.all():
        base_return = investment.instrument.base_return / Decimal('100')
        
        # Применяем модификатор события если оно затронуло этот инструмент
        modifier = Decimal('1')
        if event and investment.instrument in event.affected_instruments.all():
            modifier += event.return_modifier / Decimal('100')
        
        weekly_return = investment.amount * base_return * modifier
        total_return += weekly_return
    
    # Обновляем капитал
    game_session.current_capital += total_return
    game_session.current_week += 1
    
    # Проверяем завершение игры
    if game_session.current_week > game_session.total_weeks:
        game_session.is_finished = True
    
    game_session.save()
    
    # Сохраняем ход игры
    from .models import GameTurn
    GameTurn.objects.create(
        game_session=game_session,
        week_number=game_session.current_week - 1,
        event=event,
        capital_before=capital_before,
        capital_after=game_session.current_capital
    )
    
    return event, total_return

def create_sample_data():
    """Создает демо-данные для инструментов и событий"""
    
    # Инструменты
    instruments_data = [
        {
            'name': 'Сберегательный вклад',
            'instrument_type': 'deposit',
            'base_return': Decimal('0.5'),
            'risk_level': 1,
            'description': 'Надежный банковский вклад с фиксированной доходностью'
        },
        {
            'name': 'Голубые фишки',
            'instrument_type': 'stocks',
            'base_return': Decimal('1.2'),
            'risk_level': 3,
            'description': 'Акции крупных надежных компаний'
        },
        {
            'name': 'Государственные облигации',
            'instrument_type': 'bonds',
            'base_return': Decimal('0.8'),
            'risk_level': 1,
            'description': 'Облигации федерального займа'
        },
        {
            'name': 'Технологические акции',
            'instrument_type': 'stocks',
            'base_return': Decimal('2.0'),
            'risk_level': 3,
            'description': 'Акции компаний технологического сектора'
        },
        {
            'name': 'Корпоративные облигации',
            'instrument_type': 'bonds',
            'base_return': Decimal('1.0'),
            'risk_level': 2,
            'description': 'Облигации крупных корпораций'
        },
    ]
    
    for data in instruments_data:
        InvestmentInstrument.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
    
    # События
    events_data = [
        {
            'name': 'Рост рынка акций',
            'event_type': 'positive',
            'description': 'Биржевые индексы показывают значительный рост',
            'return_modifier': Decimal('1.0'),
            'affected_types': ['stocks']
        },
        {
            'name': 'Падение рынка',
            'event_type': 'negative',
            'description': 'Коррекция на фондовом рынке',
            'return_modifier': Decimal('-2.0'),
            'affected_types': ['stocks']
        },
        {
            'name': 'Изменение ключевой ставки',
            'event_type': 'neutral',
            'description': 'Центробанк изменил ключевую ставку',
            'return_modifier': Decimal('0.5'),
            'affected_types': ['deposit', 'bonds']
        },
        {
            'name': 'Экономический кризис',
            'event_type': 'negative',
            'description': 'Общее ухудшение экономической ситуации',
            'return_modifier': Decimal('-1.5'),
            'affected_types': ['stocks', 'bonds']
        },
        {
            'name': 'Технологический прорыв',
            'event_type': 'positive',
            'description': 'Инновации в технологическом секторе',
            'return_modifier': Decimal('2.5'),
            'affected_types': ['stocks']
        },
    ]
    
    for data in events_data:
        event, created = MarketEvent.objects.get_or_create(
            name=data['name'],
            defaults={
                'event_type': data['event_type'],
                'description': data['description'],
                'return_modifier': data['return_modifier']
            }
        )
        
        if created:
            instruments = InvestmentInstrument.objects.filter(
                instrument_type__in=data['affected_types']
            )
            event.affected_instruments.set(instruments)