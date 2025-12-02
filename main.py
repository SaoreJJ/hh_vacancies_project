from config import COMPANIES
from hh_api import HHAPI
from database import Database
from db_manager import DBManager
from utils import create_dotenv_file, display_results
import time


def main():
    """Основная функция программы"""
    print("=" * 60)
    print("ПРОГРАММА ДЛЯ СБОРА ВАКАНСИЙ С HH.RU")
    print("=" * 60)

    # 1. Проверка и создание .env файла
    create_dotenv_file()

    # 2. Создание базы данных и таблиц
    print("\n1. Настройка базы данных...")
    db = Database()

    if not db.create_database():
        print("Ошибка при создании базы данных. Проверьте настройки в .env файле.")
        return

    time.sleep(1)  # Даем время на создание БД

    if not db.create_tables():
        print("Ошибка при создании таблиц.")
        return

    print("База данных и таблицы готовы!")

    # 3. Получение данных с HH.ru
    print("\n2. Получение данных с сайта HH.ru...")

    # Получаем ID компаний из списка
    company_ids = [company["id"] for company in COMPANIES[:10]]  # Берем первые 10 компаний

    hh_api = HHAPI()
    employers_data = hh_api.get_all_employers_data(company_ids)

    if not employers_data:
        print("Не удалось получить данные с HH.ru. Проверьте подключение к интернету.")
        return

    # 4. Сохранение данных в БД
    print("\n3. Сохранение данных в базу данных...")
    total_vacancies = db.save_data_to_db(employers_data)
    print(f"\nСохранено {len(employers_data)} компаний и {total_vacancies} вакансий")

    # 5. Работа с данными через DBManager
    print("\n4. Работа с данными...")
    db_manager = DBManager()

    while True:
        print("\n" + "=" * 60)
        print("МЕНЮ РАБОТЫ С ВАКАНСИЯМИ")
        print("=" * 60)
        print("1. Показать компании и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Выход")
        print("-" * 60)

        choice = input("Выберите действие (1-6): ").strip()

        if choice == "1":
            data = db_manager.get_companies_and_vacancies_count()
            display_results(data, "КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")

        elif choice == "2":
            data = db_manager.get_all_vacancies()
            display_results(data, "ВСЕ ВАКАНСИИ")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f} руб.")

        elif choice == "4":
            data = db_manager.get_vacancies_with_higher_salary()
            display_results(data, "ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                data = db_manager.get_vacancies_with_keyword(keyword)
                display_results(data, f"ВАКАНСИИ ПО ЗАПРОСУ '{keyword.upper()}'")
            else:
                print("Ключевое слово не введено!")

        elif choice == "6":
            print("Выход из программы. До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 6.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()