#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investment_game.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Переносим создание тестовых данных в отдельную команду
    if len(sys.argv) == 2 and sys.argv[1] == 'migrate':
        # Выполняем миграции сначала
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Затем создаем тестовые данные
        from django.core.management import call_command
        call_command('create_sample_data')
    else:
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()