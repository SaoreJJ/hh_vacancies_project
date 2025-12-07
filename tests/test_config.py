import pytest
from src.config import COMPANIES, HH_API_URL


def test_config_structure():
    """Тест структуры конфига без проверки конкретных значений из .env"""
    # Проверяем, что HH_API_URL корректный
    assert HH_API_URL == "https://api.hh.ru/"

    # Проверяем, что список компаний не пустой
    assert len(COMPANIES) > 0

    # Проверяем структуру компаний
    for company in COMPANIES:
        assert 'id' in company
        assert 'name' in company
        assert isinstance(company['id'], str)
        assert isinstance(company['name'], str)
        assert company['id'].strip() != ""
        assert company['name'].strip() != ""

    # Проверяем уникальность ID
    ids = [company['id'] for company in COMPANIES]
    assert len(ids) == len(set(ids))


def test_config_variables_exist():
    """Просто проверяем, что переменные существуют и имеют правильный тип"""
    from src.config import (
        DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,
        HH_API_URL, COMPANIES
    )

    # Все переменные должны существовать и быть строкового типа
    assert isinstance(DB_NAME, str)
    assert isinstance(DB_USER, str)
    assert isinstance(DB_PASSWORD, str)
    assert isinstance(DB_HOST, str)
    assert isinstance(DB_PORT, str)
    assert isinstance(HH_API_URL, str)
    assert isinstance(COMPANIES, list)

    # Проверяем, что порт можно преобразовать в число
    assert DB_PORT.isdigit()
    port_num = int(DB_PORT)
    assert 1 <= port_num <= 65535


def test_companies_list_content():
    """Тест содержания списка компаний"""
    from src.config import COMPANIES

    # Проверяем несколько известных компаний из списка
    company_names = [company['name'] for company in COMPANIES]

    # Проверяем, что некоторые ожидаемые компании присутствуют
    expected_companies = ['Яндекс', 'VK', 'Сбер', 'Тинькофф', 'Ozon']
    for expected in expected_companies:
        assert any(expected in name for name in company_names), f"{expected} не найден в списке компаний"

    # Проверяем, что все ID состоят из цифр
    for company in COMPANIES:
        company_id = company['id']
        assert company_id.isdigit() or company_id.replace('-',
                                                          '').isdigit(), f"ID {company_id} должен содержать только цифры"


def test_hh_api_url():
    """Тест URL API"""
    from src.config import HH_API_URL
    assert HH_API_URL == "https://api.hh.ru/"
    assert HH_API_URL.startswith('https://')
    assert HH_API_URL.endswith('/')