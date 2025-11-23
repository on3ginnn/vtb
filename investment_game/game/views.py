from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import GameSession, Investment, InvestmentInstrument, GameTurn
from .forms import InvestmentForm, InvestmentDistributionForm
from .utils import calculate_weekly_returns

def index(request):
    if request.user.is_authenticated:
        try:
            game_session = GameSession.objects.filter(
                user=request.user, 
                is_finished=False
            ).first()
            
            if not game_session:
                game_session = GameSession.objects.create(
                    user=request.user,
                    current_capital=Decimal('10000')
                )
                default_instruments = InvestmentInstrument.objects.all()[:3]
                for instrument in default_instruments:
                    Investment.objects.create(
                        game_session=game_session,
                        instrument=instrument,
                        amount=Decimal('0')
                    )
            
            context = {
                'game_session': game_session,
                'investments': game_session.investments.all(),
                'available_capital': game_session.get_available_capital(),
            }
        except:
            context = {}
    else:
        context = {}
    
    return render(request, 'game/index.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Регистрация успешна!')
                return redirect('game:game')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def game_view(request):
    # Проверяем, есть ли незавершённая игра
    game_session = GameSession.objects.filter(
        user=request.user, 
        is_finished=False
    ).first()

    # Если незавершённой игры нет → отправляем на результаты
    if not game_session:
        finished_game = GameSession.objects.filter(
            user=request.user
        ).order_by('-created_at').first()

        return redirect('game:results')

    # --- Дальше как у тебя ---
    if request.method == 'POST' and 'next_week' in request.POST:
        event, weekly_return = calculate_weekly_returns(game_session)
        
        messages.info(
            request,
            f"Неделя {game_session.current_week - 1} завершена. "
            f"Доходность: {weekly_return:.2f}₽"
        )
        if event:
            messages.warning(
                request,
                f"Событие: {event.name}. {event.description}"
            )

    context = {
        'game_session': game_session,
        'investments': game_session.investments.all(),
        'turns': game_session.turns.all().order_by('-week_number'),
        'available_capital': game_session.get_available_capital(),
    }
    return render(request, 'game/game.html', context)



@login_required
def invest_view(request):
    game_session = get_object_or_404(
        GameSession, 
        user=request.user, 
        is_finished=False
    )
    
    if request.method == 'POST':
        form = InvestmentDistributionForm(request.POST, game_session=game_session)
        if form.is_valid():
            with transaction.atomic():
                for investment in game_session.investments.all():
                    field_name = f"instrument_{investment.instrument.id}"
                    new_amount = form.cleaned_data.get(field_name, Decimal('0'))
                    investment.amount = new_amount
                    investment.save()
            
            messages.success(request, 'Инвестиции успешно распределены!')
            return redirect('game:game')   # ✅ исправлено!
    else:
        form = InvestmentDistributionForm(game_session=game_session)
    
    context = {
        'form': form,
        'game_session': game_session,
        'available_capital': game_session.get_available_capital(),
    }
    return render(request, 'game/invest.html', context)


@login_required
def results_view(request):
    # Берём последнюю завершённую игру
    game_session = GameSession.objects.filter(
        user=request.user,
        is_finished=True
    ).order_by('-finished_at').first()

    if not game_session:
        messages.error(request, "Нет завершённых игр.")
        return redirect('game:game')

    total_profit = game_session.current_capital - game_session.initial_capital
    profit_percentage = (total_profit / game_session.initial_capital) * 100

    context = {
        'game_session': game_session,
        'total_profit': total_profit,
        'profit_percentage': profit_percentage,
        'investments': game_session.investments.all(),
        'turns': game_session.turns.all().order_by('week_number'),
    }
    return render(request, 'game/result.html', context)



@login_required
def history_view(request):
    game_sessions = GameSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'game/history.html', {'game_sessions': game_sessions})


@login_required
def new_game_view(request):
    current_game = GameSession.objects.filter(user=request.user, is_finished=False).first()
    if current_game:
        current_game.is_finished = True
        current_game.save()
    
    game_session = GameSession.objects.create(
        user=request.user,
        current_capital=Decimal('10000')
    )
    
    default_instruments = InvestmentInstrument.objects.all()[:3]
    for instrument in default_instruments:
        Investment.objects.create(
            game_session=game_session,
            instrument=instrument,
            amount=Decimal('0')
        )
    
    messages.success(request, 'Новая игра начата!')
    return redirect('game:game')
