from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.game_view, name='game'),
    path('invest/', views.invest_view, name='invest'),
    path('results/', views.results_view, name='results'),
    path('history/', views.history_view, name='history'),
    path('new/', views.new_game_view, name='new_game'),
]
