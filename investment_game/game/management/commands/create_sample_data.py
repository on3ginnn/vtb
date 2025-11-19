import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from game.utils import create_sample_data

class Command(BaseCommand):
    help = 'Создает тестового пользователя и демо-данные для игры'

    def handle(self, *args, **options):
        # Создаем тестового пользователя
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user('testuser', password='testpass123')
            self.stdout.write(
                self.style.SUCCESS('Создан тестовый пользователь: testuser / testpass123')
            )
        else:
            self.stdout.write('Тестовый пользователь уже существует')
        
        # Создаем демо-данные
        create_sample_data()
        self.stdout.write(
            self.style.SUCCESS('Демо-данные успешно созданы')
        )