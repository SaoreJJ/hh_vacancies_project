import os
from typing import List, Dict, Any


def create_dotenv_file() -> None:
    """
    Создание файла .env с настройками подключения к БД
    """
    env_content = """# Настройки подключения к PostgreSQL
DB_NAME=hh_vacancies
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
"""

    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("Файл .env создан. Пожалуйста, настройте параметры подключения к БД.")
    else:
        print("Файл .env уже существует.")


def display_results(data: List[Dict[str, Any]], title: str = "") -> None:
    """
    Красивое отображение результатов

    Args:
        data (List[Dict[str, Any]]): Данные для отображения
        title (str): Заголовок для вывода
    """
    if title:
        print(f"\n{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}")

    if not data:
        print("Нет данных для отображения")
        return

    for i, item in enumerate(data, 1):
        if 'vacancies_count' in item:
            # Формат для компаний и количества вакансий
            print(f"{i:2}. {item['company']:<40} | Вакансий: {item['vacancies_count']}")
        elif 'salary' in item:
            # Формат для вакансий
            print(f"{i:2}. {item['company']:<25} | {item['vacancy']:<40}")
            print(f"     Зарплата: {item['salary']}")
            print(f"     Ссылка: {item['url']}")
            print("-" * 60)

    print(f"\nВсего записей: {len(data)}")