import os
import sys
from pathlib import Path

# Добавляем родительскую директорию в sys.path для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

DB_NAME = os.getenv('DB_NAME', 'hh_vacancies')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

HH_API_URL = "https://api.hh.ru/"

# Список интересных компаний (можно изменить)
COMPANIES = [
    {"id": "1740", "name": "Яндекс"},  # Яндекс
    {"id": "15478", "name": "VK"},  # VK
    {"id": "3529", "name": "Сбер"},  # Сбер
    {"id": "78638", "name": "Тинькофф"},  # Тинькофф
    {"id": "2180", "name": "Ozon"},  # Ozon
    {"id": "87021", "name": "Wildberries"},  # Wildberries
    {"id": "4934", "name": "Билайн"},  # Билайн
    {"id": "3776", "name": "МТС"},  # МТС
    {"id": "4181", "name": "Ростелеком"},  # Ростелеком
    {"id": "1122462", "name": "Сбермаркет"},  # Сбермаркет
    {"id": "1057", "name": "Касперский"},  # Лаборатория Касперского
    {"id": "907345", "name": "2ГИС"}  # 2ГИС
]