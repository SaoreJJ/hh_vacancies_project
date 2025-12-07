import pytest
from unittest.mock import mock_open, patch
from utils import create_dotenv_file, display_results


def test_display_results_empty():
    """Тест отображения пустых результатов"""
    # Просто проверяем что функция не падает
    display_results([])
    display_results([], "Test Title")


def test_display_results_companies(capsys):
    """Тест отображения компаний"""
    data = [
        {'company': 'Company A', 'vacancies_count': 10},
        {'company': 'Company B', 'vacancies_count': 5}
    ]
    
    display_results(data, "Companies")
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Companies" in output
    assert "Company A" in output
    assert "Company B" in output
    assert "Вакансий: 10" in output
    assert "Всего записей: 2" in output


def test_display_results_vacancies(capsys):
    """Тест отображения вакансий"""
    data = [
        {
            'company': 'Company A',
            'vacancy': 'Python Developer',
            'salary': 'от 100000 до 150000 RUR',
            'url': 'http://test.com'
        }
    ]
    
    display_results(data, "Vacancies")
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Vacancies" in output
    assert "Company A" in output
    assert "Python Developer" in output
    assert "от 100000 до 150000 RUR" in output
    assert "http://test.com" in output


@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open)
def test_create_dotenv_file_new(mock_file, mock_exists):
    """Тест создания нового .env файла"""
    mock_exists.return_value = False
    
    create_dotenv_file()
    
    mock_file.assert_called_once_with('.env', 'w', encoding='utf-8')
    
    # Проверяем что записывается правильное содержимое
    handle = mock_file()
    written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
    
    assert "DB_NAME=" in written_content
    assert "DB_USER=" in written_content
    assert "DB_PASSWORD=" in written_content
    assert "HH_API_URL=" not in written_content  # Это должно быть в config.py


@patch('os.path.exists')
def test_create_dotenv_file_exists(mock_exists, capsys):
    """Тест когда .env файл уже существует"""
    mock_exists.return_value = True
    
    create_dotenv_file()
    
    captured = capsys.readouterr()
    assert "Файл .env уже существует" in captured.out