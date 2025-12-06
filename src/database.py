import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import OperationalError, Error
from typing import List, Dict, Any, Optional
try:
    from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
except ImportError:
    from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class Database:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self):
        self.connection_params = {
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'port': DB_PORT
        }
        self.connection = None

    def connect(self, dbname: Optional[str] = None) -> bool:
        """
        Подключение к базе данных

        Args:
            dbname (Optional[str]): Имя базы данных (если None, используется из конфига)

        Returns:
            bool: True если подключение успешно, False в противном случае
        """
        params = self.connection_params.copy()
        if dbname:
            params['dbname'] = dbname

        try:
            self.connection = psycopg2.connect(**params)
            self.connection.autocommit = True
            return True
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def create_database(self) -> bool:
        """
        Создание базы данных

        Returns:
            bool: True если база создана успешно
        """
        # Подключаемся к базе данных postgres для создания новой БД
        params = self.connection_params.copy()
        params['dbname'] = 'postgres'

        try:
            conn = psycopg2.connect(**params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Проверяем существование базы данных
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"База данных '{DB_NAME}' создана успешно")
            else:
                print(f"База данных '{DB_NAME}' уже существует")

            cursor.close()
            conn.close()
            return True

        except Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Создание таблиц в базе данных

        Returns:
            bool: True если таблицы созданы успешно
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()

            # Создание таблицы employers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url VARCHAR(500),
                    description TEXT,
                    area VARCHAR(100)
                )
            """)

            # Создание таблицы vacancies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id INTEGER PRIMARY KEY,
                    employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE,
                    title VARCHAR(500) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    url VARCHAR(500) NOT NULL,
                    experience VARCHAR(100),
                    requirement TEXT,
                    responsibility TEXT
                )
            """)

            cursor.close()
            print("Таблицы созданы успешно")
            return True

        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()

    def insert_employer(self, employer_data: Dict) -> bool:
        """
        Вставка данных о работодателе

        Args:
            employer_data (Dict): Данные работодателя

        Returns:
            bool: True если вставка успешна
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                INSERT INTO employers (employer_id, name, url, description, area)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (employer_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    description = EXCLUDED.description,
                    area = EXCLUDED.area
            """, (
                employer_data.get('id'),
                employer_data.get('name'),
                employer_data.get('alternate_url'),
                employer_data.get('description', '')[:1000],  # Ограничиваем длину
                employer_data.get('area', {}).get('name', '')
            ))

            cursor.close()
            return True

        except Error as e:
            print(f"Ошибка при вставке работодателя: {e}")
            return False

    def insert_vacancy(self, vacancy_data: Dict, employer_id: int) -> bool:
        """
        Вставка данных о вакансии

        Args:
            vacancy_data (Dict): Данные вакансии
            employer_id (int): ID работодателя

        Returns:
            bool: True если вставка успешна
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()

            # Обработка зарплаты
            salary = vacancy_data.get('salary')
            salary_from = salary.get('from') if salary else None
            salary_to = salary.get('to') if salary else None
            currency = salary.get('currency') if salary else None

            cursor.execute("""
                INSERT INTO vacancies (
                    vacancy_id, employer_id, title, salary_from, salary_to, 
                    currency, url, experience, requirement, responsibility
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    salary_from = EXCLUDED.salary_from,
                    salary_to = EXCLUDED.salary_to,
                    currency = EXCLUDED.currency,
                    url = EXCLUDED.url,
                    experience = EXCLUDED.experience,
                    requirement = EXCLUDED.requirement,
                    responsibility = EXCLUDED.responsibility
            """, (
                vacancy_data.get('id'),
                employer_id,
                vacancy_data.get('name'),
                salary_from,
                salary_to,
                currency,
                vacancy_data.get('alternate_url'),
                vacancy_data.get('experience', {}).get('name', ''),
                vacancy_data.get('snippet', {}).get('requirement', '')[:1000],
                vacancy_data.get('snippet', {}).get('responsibility', '')[:1000]
            ))

            cursor.close()
            return True

        except Error as e:
            print(f"Ошибка при вставке вакансии: {e}")
            return False

    def save_data_to_db(self, employers_data: Dict[str, Any]) -> int:
        """
        Сохранение всех данных в базу данных

        Args:
            employers_data (Dict[str, Any]): Данные о работодателях и вакансиях

        Returns:
            int: Количество сохраненных вакансий
        """
        total_vacancies = 0

        for emp_id, data in employers_data.items():
            employer = data['employer']
            vacancies = data['vacancies']

            # Сохраняем работодателя
            if self.insert_employer(employer):
                print(f"Работодатель {employer.get('name')} сохранен")

                # Сохраняем вакансии
                vacancy_count = 0
                for vacancy in vacancies:
                    if self.insert_vacancy(vacancy, int(emp_id)):
                        vacancy_count += 1

                total_vacancies += vacancy_count
                print(f"Сохранено {vacancy_count} вакансий")

        if self.connection:
            self.connection.close()

        return total_vacancies