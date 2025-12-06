import sys
import os

# Добавляем пути для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)


def test_main_import():
    """Тест импорта main.py"""
    try:
        import main
        print("✓ main.py успешно импортирован")
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта main.py: {e}")
        return False


def test_main_function_exists():
    """Тест, что функция main существует"""
    try:
        from main import main
        print("✓ Функция main() существует")
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта функции main: {e}")
        return False


def test_main_has_docstring():
    """Тест наличия документации у функции main"""
    try:
        from main import main
        if main.__doc__:
            print(f"✓ Функция main() имеет документацию ({len(main.__doc__)} символов)")
            return True
        else:
            print("⚠  Функция main() не имеет документации")
            return False
    except Exception as e:
        print(f"✗ Ошибка проверки документации: {e}")
        return False


def test_main_file_exists():
    """Тест существования файла main.py"""
    main_file = os.path.join(project_root, 'main.py')
    if os.path.exists(main_file):
        print(f"✓ Файл main.py существует ({os.path.getsize(main_file)} байт)")
        return True
    else:
        print("✗ Файл main.py не существует")
        return False


def test_main_structure():
    """Тест структуры main.py"""
    main_file = os.path.join(project_root, 'main.py')

    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем ключевые элементы
        checks = [
            ('def main():', "определение функции main"),
            ('if __name__ == "__main__":', "блок запуска"),
            ('main()', "вызов функции main"),
            ('while True:', "основной цикл"),
            ('МЕНЮ РАБОТЫ С ВАКАНСИЯМИ', "заголовок меню"),
            ('6. Выход', "пункт выхода из меню")
        ]

        all_passed = True
        for text, description in checks:
            if text in content:
                print(f"✓ Найден: {description}")
            else:
                print(f"✗ Не найден: {description}")
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"✗ Ошибка чтения файла main.py: {e}")
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ MAIN.PY")
    print("=" * 60)

    tests = [
        ("Существование файла", test_main_file_exists),
        ("Импорт модуля", test_main_import),
        ("Наличие функции main", test_main_function_exists),
        ("Документация функции", test_main_has_docstring),
        ("Структура файла", test_main_structure),
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