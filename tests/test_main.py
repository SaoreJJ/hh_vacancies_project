import pytest
from unittest.mock import Mock, patch
import builtins


@patch('main.create_dotenv_file')
@patch('main.Database')
@patch('main.HHAPI')
@patch('main.DBManager')
@patch('main.display_results')
@patch('main.time.sleep')
def test_main_menu_flow(mock_sleep, mock_display, mock_dbmanager, mock_hhapi,
                        mock_database, mock_create_dotenv):
    """Тест основного потока программы"""
    # Мокаем ввод пользователя: опция 1, Enter для продолжения, затем выход
    # Каждая опция в меню требует Enter для продолжения после отображения результатов
    input_values = ['1', '', '6']  # Выбор 1, Enter, выбор 6

    with patch('builtins.input', side_effect=input_values):
        # Мокаем Database
        mock_db_instance = Mock()
        mock_db_instance.create_database.return_value = True
        mock_db_instance.create_tables.return_value = True
        mock_db_instance.save_data_to_db.return_value = 50
        mock_database.return_value = mock_db_instance

        # Мокаем HHAPI
        mock_api_instance = Mock()
        mock_api_instance.get_all_employers_data.return_value = {
            '1': {'employer': {'name': 'Test'}, 'vacancies': []}
        }
        mock_hhapi.return_value = mock_api_instance

        # Мокаем DBManager
        mock_manager_instance = Mock()
        mock_manager_instance.get_companies_and_vacancies_count.return_value = [
            {'company': 'Test', 'vacancies_count': 10}
        ]
        mock_dbmanager.return_value = mock_manager_instance

        # Импортируем и запускаем main
        from main import main
        main()

        # Проверяем вызовы
        mock_create_dotenv.assert_called_once()
        mock_database.assert_called_once()
        mock_db_instance.create_database.assert_called_once()
        mock_db_instance.create_tables.assert_called_once()

        # Проверяем что отображались результаты
        mock_display.assert_called_once()

        # Проверяем что DBManager вызывался
        mock_manager_instance.get_companies_and_vacancies_count.assert_called_once()


@patch('main.create_dotenv_file')
@patch('main.Database')
@patch('main.time.sleep')
def test_main_database_creation_failure(mock_sleep, mock_database, mock_create_dotenv):
    """Тест неудачного создания БД"""
    mock_db_instance = Mock()
    mock_db_instance.create_database.return_value = False
    mock_database.return_value = mock_db_instance

    # Не нужно мокать input, т.к. программа должна завершиться до меню
    from main import main
    main()

    mock_create_dotenv.assert_called_once()
    mock_db_instance.create_database.assert_called_once()
    mock_db_instance.create_tables.assert_not_called()


@patch('main.create_dotenv_file')
@patch('main.Database')
@patch('main.HHAPI')
@patch('main.DBManager')
@patch('main.display_results')
@patch('main.time.sleep')
def test_main_all_menu_options(mock_sleep, mock_display, mock_dbmanager,
                               mock_hhapi, mock_database, mock_create_dotenv):
    """Тест всех опций меню"""
    # Симуляция выбора всех опций по порядку
    input_values = [
        '1', '',  # Компании и вакансии + Enter
        '2', '',  # Все вакансии + Enter
        '3', '',  # Средняя зарплата + Enter
        '4', '',  # Вакансии выше средней + Enter
        '5', 'python', '',  # Поиск по слову + Enter
        '6'  # Выход
    ]

    with patch('builtins.input', side_effect=input_values):
        # Настраиваем моки
        mock_db_instance = Mock()
        mock_db_instance.create_database.return_value = True
        mock_db_instance.create_tables.return_value = True
        mock_db_instance.save_data_to_db.return_value = 10
        mock_database.return_value = mock_db_instance

        mock_api_instance = Mock()
        mock_api_instance.get_all_employers_data.return_value = {
            '1': {'employer': {}, 'vacancies': []}
        }
        mock_hhapi.return_value = mock_api_instance

        # Настраиваем DBManager для разных методов
        mock_manager_instance = Mock()
        mock_manager_instance.get_companies_and_vacancies_count.return_value = []
        mock_manager_instance.get_all_vacancies.return_value = []
        mock_manager_instance.get_avg_salary.return_value = 100000.0
        mock_manager_instance.get_vacancies_with_higher_salary.return_value = []
        mock_manager_instance.get_vacancies_with_keyword.return_value = []
        mock_dbmanager.return_value = mock_manager_instance

        from main import main
        main()

        # Проверяем что все методы DBManager были вызваны
        assert mock_manager_instance.get_companies_and_vacancies_count.called
        assert mock_manager_instance.get_all_vacancies.called
        assert mock_manager_instance.get_avg_salary.called
        assert mock_manager_instance.get_vacancies_with_higher_salary.called
        assert mock_manager_instance.get_vacancies_with_keyword.called


@patch('main.create_dotenv_file')
@patch('main.Database')
@patch('main.HHAPI')
@patch('main.time.sleep')
def test_main_api_failure(mock_sleep, mock_hhapi, mock_database, mock_create_dotenv):
    """Тест неудачного получения данных с API"""
    mock_db_instance = Mock()
    mock_db_instance.create_database.return_value = True
    mock_db_instance.create_tables.return_value = True
    mock_database.return_value = mock_db_instance

    mock_api_instance = Mock()
    mock_api_instance.get_all_employers_data.return_value = {}  # Пустой результат
    mock_hhapi.return_value = mock_api_instance

    from main import main
    main()

    mock_api_instance.get_all_employers_data.assert_called_once()
    mock_db_instance.save_data_to_db.assert_not_called()  # Не должно сохранять


@patch('main.create_dotenv_file')
@patch('main.Database')
@patch('main.HHAPI')
@patch('main.DBManager')
@patch('main.time.sleep')
def test_main_invalid_menu_option(mock_sleep, mock_dbmanager, mock_hhapi,
                                  mock_database, mock_create_dotenv):
    """Тест неверного выбора в меню"""
    # Симуляция: неверный выбор, затем выход
    input_values = ['invalid', '7', '6']

    with patch('builtins.input', side_effect=input_values):
        mock_db_instance = Mock()
        mock_db_instance.create_database.return_value = True
        mock_db_instance.create_tables.return_value = True
        mock_db_instance.save_data_to_db.return_value = 10
        mock_database.return_value = mock_db_instance

        mock_api_instance = Mock()
        mock_api_instance.get_all_employers_data.return_value = {'1': {}}
        mock_hhapi.return_value = mock_api_instance

        from main import main
        main()

        # Программа не должна упасть на неверном вводе
        # Должна просто продолжить работу


def test_main_import():
    """Тест что модуль main импортируется без ошибок"""
    from main import main
    assert callable(main)