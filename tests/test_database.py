import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from src.database import Database


class TestDatabase:
    """Тесты для класса Database"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.db = Database()
        self.db.connection_params = {
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'host': 'localhost',
            'port': '5432'
        }

    @patch('src.database.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Тест успешного подключения к базе данных"""
        # Arrange
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Act
        result = self.db.connect()

        # Assert
        assert result is True
        mock_connect.assert_called_once_with(**self.db.connection_params)
        assert self.db.connection == mock_conn
        assert mock_conn.autocommit is True

    @patch('src.database.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Тест неудачного подключения к базе данных"""
        # Arrange
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        # Act
        result = self.db.connect()

        # Assert
        assert result is False
        assert self.db.connection is None

    def test_connect_with_custom_dbname(self):
        """Тест подключения с указанием имени базы данных"""
        # Arrange
        custom_dbname = 'custom_db'

        with patch('src.database.psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            # Act
            result = self.db.connect(custom_dbname)

            # Assert
            assert result is True
            expected_params = self.db.connection_params.copy()
            expected_params['dbname'] = custom_dbname
            mock_connect.assert_called_once_with(**expected_params)

    @patch('src.database.psycopg2.connect')
    def test_create_database_new(self, mock_connect):
        """Тест создания новой базы данных"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # База не существует

        # Важно: замокать DB_NAME, чтобы тест использовал правильное имя
        with patch('src.database.DB_NAME', 'test_db'):
            # Act
            result = self.db.create_database()

        # Assert
        assert result is True
        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'"
        )
        mock_cursor.execute.assert_any_call(
            "CREATE DATABASE test_db"
        )

    @patch('src.database.psycopg2.connect')
    def test_create_database_exists(self, mock_connect):
        """Тест, когда база данных уже существует"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # База существует

        # Важно: замокать DB_NAME, чтобы тест использовал правильное имя
        with patch('src.database.DB_NAME', 'test_db'):
            # Act
            result = self.db.create_database()

        # Assert
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'"
        )
        # CREATE DATABASE не должен вызываться
        assert mock_cursor.execute.call_count == 1

    @patch.object(Database, 'connect')
    def test_create_tables_success(self, mock_connect):
        """Тест успешного создания таблиц"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = True
        self.db.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Act
        result = self.db.create_tables()

        # Assert
        assert result is True
        # Проверяем, что было вызвано 2 CREATE TABLE
        assert mock_cursor.execute.call_count == 2

        # Проверяем, что среди вызовов есть создание таблиц employers и vacancies
        calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
        assert any('CREATE TABLE IF NOT EXISTS employers' in str(call) for call in calls)
        assert any('CREATE TABLE IF NOT EXISTS vacancies' in str(call) for call in calls)

        mock_conn.close.assert_called_once()

    @patch.object(Database, 'connect')
    def test_create_tables_connection_failed(self, mock_connect):
        """Тест создания таблиц при неудачном подключении"""
        # Arrange
        mock_connect.return_value = False

        # Act
        result = self.db.create_tables()

        # Assert
        assert result is False

    @patch.object(Database, 'connect')
    def test_insert_employer_success(self, mock_connect):
        """Тест успешной вставки работодателя"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()
        mock_cursor = Mock()
        self.db.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        employer_data = {
            'id': 123,
            'name': 'Test Company',
            'alternate_url': 'http://test.com',
            'description': 'Test description' * 100,  # Длинное описание
            'area': {'name': 'Moscow'}
        }

        # Act
        result = self.db.insert_employer(employer_data)

        # Assert
        assert result is True
        mock_cursor.execute.assert_called_once()

        # Проверяем, что в вызове execute переданы правильные параметры
        call_args = mock_cursor.execute.call_args[0]
        assert 'INSERT INTO employers' in call_args[0]
        assert call_args[1][0] == 123  # employer_id
        assert call_args[1][1] == 'Test Company'  # name

    @patch.object(Database, 'connect')
    def test_insert_vacancy_success(self, mock_connect):
        """Тест успешной вставки вакансии"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()
        mock_cursor = Mock()
        self.db.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        vacancy_data = {
            'id': 456,
            'name': 'Test Vacancy',
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUB'},
            'alternate_url': 'http://test.com/vacancy',
            'experience': {'name': '1-3 years'},
            'snippet': {
                'requirement': 'Test requirement',
                'responsibility': 'Test responsibility'
            }
        }

        # Act
        result = self.db.insert_vacancy(vacancy_data, 123)

        # Assert
        assert result is True
        mock_cursor.execute.assert_called_once()

        # Проверяем параметры
        call_args = mock_cursor.execute.call_args[0]
        assert 'INSERT INTO vacancies' in call_args[0]
        assert call_args[1][0] == 456  # vacancy_id
        assert call_args[1][1] == 123  # employer_id
        assert call_args[1][2] == 'Test Vacancy'  # title

    @patch.object(Database, 'insert_employer')
    @patch.object(Database, 'insert_vacancy')
    def test_save_data_to_db(self, mock_insert_vacancy, mock_insert_employer):
        """Тест сохранения всех данных в БД"""
        # Arrange
        mock_insert_employer.return_value = True
        mock_insert_vacancy.return_value = True

        employers_data = {
            '123': {
                'employer': {'id': 123, 'name': 'Company 1'},
                'vacancies': [
                    {'id': 1, 'name': 'Vacancy 1'},
                    {'id': 2, 'name': 'Vacancy 2'}
                ]
            },
            '456': {
                'employer': {'id': 456, 'name': 'Company 2'},
                'vacancies': [
                    {'id': 3, 'name': 'Vacancy 3'}
                ]
            }
        }

        # Act
        result = self.db.save_data_to_db(employers_data)

        # Assert
        assert result == 3  # Всего 3 вакансии
        assert mock_insert_employer.call_count == 2
        assert mock_insert_vacancy.call_count == 3

        # Проверяем, что методы вызывались с правильными аргументами
        # Первый вызов insert_employer
        first_employer_call = mock_insert_employer.call_args_list[0]
        assert first_employer_call[0][0]['id'] == 123

        # Первый вызов insert_vacancy
        first_vacancy_call = mock_insert_vacancy.call_args_list[0]
        assert first_vacancy_call[0][0]['id'] == 1
        assert first_vacancy_call[0][1] == 123  # employer_id