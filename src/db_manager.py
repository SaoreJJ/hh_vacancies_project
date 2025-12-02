import psycopg2
from typing import List, Dict, Any, Optional
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class DBManager:
    """
    Класс для управления данными в базе данных PostgreSQL

    Предоставляет методы для выполнения различных запросов к базе данных
    с информацией о работодателях и вакансиях.
    """

    def __init__(self):
        """Инициализация подключения к базе данных"""
        self.conn_params = {
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'port': DB_PORT
        }
        self.connection = None

    def connect(self) -> bool:
        """
        Установка соединения с базой данных

        Returns:
            bool: True если соединение установлено успешно, False в противном случае
        """
        try:
            self.connection = psycopg2.connect(**self.conn_params)
            return True
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def disconnect(self) -> None:
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании

        Returns:
            List[Dict[str, Any]]: Список словарей с названием компании и количеством вакансий
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.employer_id, e.name
                    ORDER BY vacancy_count DESC
                """)

                result = []
                for row in cursor.fetchall():
                    result.append({
                        'company': row[0],
                        'vacancies_count': row[1]
                    })

                return result

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            self.disconnect()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.name as company_name,
                        v.title as vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    ORDER BY e.name, v.title
                """)

                result = []
                for row in cursor.fetchall():
                    # Форматирование зарплаты
                    salary_info = "Не указана"
                    if row[2] or row[3]:
                        salary_parts = []
                        if row[2]:
                            salary_parts.append(f"от {row[2]}")
                        if row[3]:
                            salary_parts.append(f"до {row[3]}")
                        salary_info = f"{' '.join(salary_parts)} {row[4] or ''}"

                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            self.disconnect()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям

        Returns:
            float: Средняя зарплата. Возвращает 0.0 если нет данных
        """
        if not self.connect():
            return 0.0

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """)

                result = cursor.fetchone()[0]
                return float(result) if result else 0.0

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return 0.0
        finally:
            self.disconnect()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям

        Returns:
            List[Dict[str, Any]]: Список словарей с вакансиями с высокой зарплатой
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.name as company_name,
                        v.title as vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > (
                        SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                        FROM vacancies
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    )
                    ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
                """)

                result = []
                for row in cursor.fetchall():
                    # Форматирование зарплаты
                    salary_info = "Не указана"
                    if row[2] or row[3]:
                        salary_parts = []
                        if row[2]:
                            salary_parts.append(f"от {row[2]}")
                        if row[3]:
                            salary_parts.append(f"до {row[3]}")
                        salary_info = f"{' '.join(salary_parts)} {row[4] or ''}"

                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            self.disconnect()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова

        Args:
            keyword (str): Ключевое слово для поиска в названиях вакансий

        Returns:
            List[Dict[str, Any]]: Список словарей с найденными вакансиями
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.name as company_name,
                        v.title as vacancy_title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE LOWER(v.title) LIKE %s
                    ORDER BY e.name, v.title
                """, (f'%{keyword.lower()}%',))

                result = []
                for row in cursor.fetchall():
                    # Форматирование зарплаты
                    salary_info = "Не указана"
                    if row[2] or row[3]:
                        salary_parts = []
                        if row[2]:
                            salary_parts.append(f"от {row[2]}")
                        if row[3]:
                            salary_parts.append(f"до {row[3]}")
                        salary_info = f"{' '.join(salary_parts)} {row[4] or ''}"

                    result.append({
                        'company': row[0],
                        'vacancy': row[1],
                        'salary': salary_info,
                        'url': row[5]
                    })

                return result

        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            self.disconnect()