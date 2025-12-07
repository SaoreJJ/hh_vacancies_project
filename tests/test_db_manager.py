
import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from src.db_manager import DBManager


class TestDBManager:
    """Тесты для класса DBManager"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.db_manager = DBManager()
        self.db_manager.conn_params = {
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'host': 'localhost',
            'port': '5432'
        }

    @patch('src.db_manager.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Тест успешного подключения"""
        # Arrange
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Act
        result = self.db_manager.connect()

        # Assert
        assert result is True
        mock_connect.assert_called_once_with(**self.db_manager.conn_params)
        assert self.db_manager.connection == mock_conn

    @patch('src.db_manager.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Тест неудачного подключения"""
        # Arrange
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        # Act
        result = self.db_manager.connect()

        # Assert
        assert result is False
        assert self.db_manager.connection is None

    def test_disconnect(self):
        """Тест закрытия соединения"""
        # Arrange
        mock_conn = Mock()
        self.db_manager.connection = mock_conn

        # Act
        self.db_manager.disconnect()

        # Assert
        mock_conn.close.assert_called_once()

    def test_disconnect_no_connection(self):
        """Тест закрытия соединения, когда его нет"""
        # Arrange
        self.db_manager.connection = None

        # Act
        self.db_manager.disconnect()

        # Assert
        # Ничего не должно сломаться

    @patch.object(DBManager, 'connect')
    def test_get_companies_and_vacancies_count_success(self, mock_connect):
        """Тест получения компаний и количества вакансий"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        # Создаем MagicMock для курсора, который будет поддерживать контекстный менеджер
        mock_cursor = MagicMock()
        # Настраиваем возвращаемые значения для контекстного менеджера
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        # Настраиваем, чтобы mock_conn.cursor() возвращал наш mock_cursor
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchall.return_value = [
            ('Company 1', 5),
            ('Company 2', 3),
            ('Company 3', 0)
        ]

        # Act
        result = self.db_manager.get_companies_and_vacancies_count()

        # Assert
        assert len(result) == 3
        assert result[0]['company'] == 'Company 1'
        assert result[0]['vacancies_count'] == 5
        assert result[1]['company'] == 'Company 2'
        assert result[1]['vacancies_count'] == 3
        assert result[2]['company'] == 'Company 3'
        assert result[2]['vacancies_count'] == 0

    @patch.object(DBManager, 'connect')
    def test_get_companies_and_vacancies_count_connection_failed(self, mock_connect):
        """Тест при неудачном подключении"""
        # Arrange
        mock_connect.return_value = False

        # Act
        result = self.db_manager.get_companies_and_vacancies_count()

        # Assert
        assert result == []

    @patch.object(DBManager, 'connect')
    def test_get_all_vacancies_success(self, mock_connect):
        """Тест получения всех вакансий"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchall.return_value = [
            ('Company 1', 'Python Developer', 100000, 150000, 'RUB', 'http://test.com/1'),
            ('Company 2', 'Data Scientist', None, 200000, 'RUB', 'http://test.com/2'),
            ('Company 3', 'DevOps Engineer', 150000, None, 'USD', 'http://test.com/3'),
            ('Company 4', 'Frontend Developer', None, None, None, 'http://test.com/4')
        ]

        # Act
        result = self.db_manager.get_all_vacancies()

        # Assert
        assert len(result) == 4
        assert result[0]['company'] == 'Company 1'
        assert result[0]['vacancy'] == 'Python Developer'
        assert result[0]['salary'] == 'от 100000 до 150000 RUB'
        assert result[1]['salary'] == 'до 200000 RUB'
        assert result[2]['salary'] == 'от 150000 USD'
        assert result[3]['salary'] == 'Не указана'

    @patch.object(DBManager, 'connect')
    def test_get_avg_salary_success(self, mock_connect):
        """Тест получения средней зарплаты"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchone.return_value = (125000.50,)

        # Act
        result = self.db_manager.get_avg_salary()

        # Assert
        assert result == 125000.50

    @patch.object(DBManager, 'connect')
    def test_get_avg_salary_no_data(self, mock_connect):
        """Тест получения средней зарплаты, когда нет данных"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchone.return_value = (None,)

        # Act
        result = self.db_manager.get_avg_salary()

        # Assert
        assert result == 0.0

    @patch.object(DBManager, 'connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchall.return_value = [
            ('Company 1', 'Senior Developer', 200000, 300000, 'RUB', 'http://test.com/1'),
            ('Company 2', 'Lead Engineer', 250000, 350000, 'RUB', 'http://test.com/2')
        ]

        # Act
        result = self.db_manager.get_vacancies_with_higher_salary()

        # Assert
        assert len(result) == 2
        assert result[0]['company'] == 'Company 1'
        assert result[0]['vacancy'] == 'Senior Developer'
        assert result[0]['salary'] == 'от 200000 до 300000 RUB'

    @patch.object(DBManager, 'connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchall.return_value = [
            ('Company 1', 'Python Developer', 100000, 150000, 'RUB', 'http://test.com/1'),
            ('Company 2', 'Python Data Scientist', 120000, 180000, 'RUB', 'http://test.com/2')
        ]

        # Act
        result = self.db_manager.get_vacancies_with_keyword('python')

        # Assert
        assert len(result) == 2
        assert all('Python' in item['vacancy'] for item in result)

    @patch.object(DBManager, 'connect')
    def test_get_vacancies_with_keyword_no_results(self, mock_connect):
        """Тест поиска вакансий, когда нет результатов"""
        # Arrange
        mock_connect.return_value = True
        mock_conn = Mock()

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor

        self.db_manager.connection = mock_conn

        mock_cursor.fetchall.return_value = []

        # Act
        result = self.db_manager.get_vacancies_with_keyword('nonexistent')

        # Assert
        assert result == []