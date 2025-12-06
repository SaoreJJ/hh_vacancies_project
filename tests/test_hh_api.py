import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from src.hh_api import HHAPI


class TestHHAPI:
    """Тесты для класса HHAPI"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.api = HHAPI()

    @patch('src.hh_api.requests.get')
    def test_get_employer_info_success(self, mock_get):
        """Тест успешного получения информации о работодателе"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123',
            'name': 'Test Company',
            'alternate_url': 'http://test.com',
            'description': 'Test description',
            'area': {'name': 'Moscow'}
        }
        mock_get.return_value = mock_response

        # Act
        result = self.api.get_employer_info('123')

        # Assert
        assert result is not None
        assert result['id'] == '123'
        assert result['name'] == 'Test Company'
        mock_get.assert_called_once_with(
            f"{self.api.base_url}employers/123",
            headers=self.api.headers
        )

    @patch('src.hh_api.requests.get')
    def test_get_employer_info_failure(self, mock_get):
        """Тест неудачного получения информации о работодателе"""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        # Act
        result = self.api.get_employer_info('123')

        # Assert
        assert result is None

    @patch('src.hh_api.requests.get')
    def test_get_employer_vacancies_single_page(self, mock_get):
        """Тест получения вакансий работодателя (одна страница)"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'id': '1', 'name': 'Vacancy 1'},
                {'id': '2', 'name': 'Vacancy 2'}
            ],
            'pages': 1,
            'page': 0
        }
        mock_get.return_value = mock_response

        # Act
        result = self.api.get_employer_vacancies('123', per_page=50)

        # Assert
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '2'

    @patch('src.hh_api.requests.get')
    def test_get_employer_vacancies_multiple_pages(self, mock_get):
        """Тест получения вакансий работодателя (несколько страниц)"""
        # Arrange
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            'items': [{'id': str(i), 'name': f'Vacancy {i}'} for i in range(1, 6)],
            'pages': 2,
            'page': 0
        }

        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            'items': [{'id': str(i), 'name': f'Vacancy {i}'} for i in range(6, 8)],
            'pages': 2,
            'page': 1
        }

        mock_get.side_effect = [mock_response_page1, mock_response_page2]

        # Act
        result = self.api.get_employer_vacancies('123', per_page=5)

        # Assert
        assert len(result) == 7  # 5 с первой страницы + 2 со второй
        assert mock_get.call_count == 2

    @patch('src.hh_api.requests.get')
    def test_get_employer_vacancies_api_error(self, mock_get):
        """Тест получения вакансий при ошибке API"""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        # Act
        result = self.api.get_employer_vacancies('123')

        # Assert
        assert result == []

    @patch.object(HHAPI, 'get_employer_info')
    @patch.object(HHAPI, 'get_employer_vacancies')
    def test_get_all_employers_data_success(self, mock_get_vacancies, mock_get_info):
        """Тест получения данных всех работодателей"""
        # Arrange
        employer_ids = ['123', '456']

        mock_get_info.side_effect = [
            {'id': '123', 'name': 'Company 1'},
            {'id': '456', 'name': 'Company 2'}
        ]

        mock_get_vacancies.side_effect = [
            [{'id': '1', 'name': 'Vacancy 1'}, {'id': '2', 'name': 'Vacancy 2'}],
            [{'id': '3', 'name': 'Vacancy 3'}]
        ]

        # Act
        result = self.api.get_all_employers_data(employer_ids)

        # Assert
        assert len(result) == 2
        assert '123' in result
        assert '456' in result
        assert result['123']['employer']['name'] == 'Company 1'
        assert len(result['123']['vacancies']) == 2
        assert len(result['456']['vacancies']) == 1

    @patch.object(HHAPI, 'get_employer_info')
    def test_get_all_employers_data_employer_failed(self, mock_get_info):
        """Тест, когда не удалось получить данные работодателя"""
        # Arrange
        employer_ids = ['123', '456']

        mock_get_info.side_effect = [
            {'id': '123', 'name': 'Company 1'},  # Успех
            None  # Ошибка для второго работодателя
        ]

        # Act
        result = self.api.get_all_employers_data(employer_ids)

        # Assert
        assert len(result) == 1
        assert '123' in result
        assert '456' not in result