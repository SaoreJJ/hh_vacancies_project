"""Рабочие тесты для utils.py"""
import sys
import os

# Добавляем пути для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, src_path)


def test_utils_imports():
    """Тест импортов utils.py"""
    print("Тест 1: Импорт модуля utils...")

    try:
        from src.utils import create_dotenv_file, display_results
        print("✓ Функции create_dotenv_file и display_results импортированы")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")

        # Попробуем альтернативный путь импорта
        try:
            # Добавляем src в путь напрямую
            import src.utils as utils_module
            print(f"✓ Модуль utils найден: {utils_module}")
            return True
        except ImportError as e2:
            print(f"✗ Альтернативный импорт тоже не сработал: {e2}")
            return False


def test_create_dotenv_file():
    """Тест функции create_dotenv_file"""
    print("\nТест 2: Функция create_dotenv_file...")

    try:
        from src.utils import create_dotenv_file

        # Сохраняем оригинальный .env если есть
        env_exists = os.path.exists('.env')
        env_backup = None

        if env_exists:
            with open('.env', 'r', encoding='utf-8') as f:
                env_backup = f.read()
            os.remove('.env')

        try:
            # Создаем временный файл
            create_dotenv_file()

            # Проверяем, что файл создан
            assert os.path.exists('.env'), "Файл .env не создан"

            # Проверяем содержимое
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'DB_NAME=' in content
                assert 'DB_USER=' in content
                assert 'DB_PASSWORD=' in content

            print("✓ Файл .env создан корректно")

            # Проверяем повторное создание (должно показать, что файл уже существует)
            create_dotenv_file()
            print("✓ Обработка существующего файла корректна")

            return True

        finally:
            # Восстанавливаем оригинальный .env
            if os.path.exists('.env'):
                os.remove('.env')
            if env_backup:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(env_backup)

    except Exception as e:
        print(f"✗ Ошибка теста create_dotenv_file: {e}")
        return False


def test_display_results():
    """Тест функции display_results"""
    print("\nТест 3: Функция display_results...")

    try:
        from src.utils import display_results

        # Тест 1: Пустые данные
        print("  Подтест 3.1: Пустые данные...")
        display_results([], "Empty Test")
        print("  ✓ Пустые данные обрабатываются")

        # Тест 2: Данные компаний
        print("  Подтест 3.2: Данные компаний...")
        companies_data = [
            {'company': 'Яндекс', 'vacancies_count': 50},
            {'company': 'Сбер', 'vacancies_count': 30},
            {'company': 'Тинькофф', 'vacancies_count': 20}
        ]
        display_results(companies_data, "Компании")
        print("  ✓ Данные компаний отображаются")

        # Тест 3: Данные вакансий
        print("  Подтест 3.3: Данные вакансий...")
        vacancies_data = [
            {
                'company': 'Яндекс',
                'vacancy': 'Python разработчик',
                'salary': 'от 200000 до 350000 RUB',
                'url': 'https://hh.ru/vacancy/123'
            },
            {
                'company': 'Сбер',
                'vacancy': 'Data Scientist',
                'salary': 'Не указана',
                'url': 'https://hh.ru/vacancy/456'
            }
        ]
        display_results(vacancies_data, "Вакансии")
        print("  ✓ Данные вакансий отображаются")

        return True

    except Exception as e:
        print(f"✗ Ошибка теста display_results: {e}")
        return False


def test_utils_module_structure():
    """Тест структуры модуля utils.py"""
    print("\nТест 4: Структура модуля utils.py...")

    try:
        # Читаем файл utils.py
        utils_file = os.path.join(src_path, 'utils.py')

        with open(utils_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем наличие функций
        assert 'def create_dotenv_file()' in content, "Функция create_dotenv_file не найдена"
        assert 'def display_results(' in content, "Функция display_results не найдена"

        # Проверяем наличие документации
        if '"""' in content:
            print("✓ Модуль имеет документацию")

        print("✓ Структура модуля utils.py корректна")
        return True

    except Exception as e:
        print(f"✗ Ошибка теста структуры: {e}")
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ UTILS.PY")
    print("=" * 60)

    tests = [
        ("Импорты", test_utils_imports),
        ("create_dotenv_file", test_create_dotenv_file),
        ("display_results", test_display_results),
        ("Структура модуля", test_utils_module_structure),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} пройден")
            else:
                failed += 1
                print(f"✗ {test_name} не пройден")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} вызвал ошибку: {e}")

    print("\n" + "=" * 60)
    print(f"ИТОГИ: {passed} пройдено, {failed} не пройдено")

    if failed == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print("⚠  Есть непройденные тесты")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)