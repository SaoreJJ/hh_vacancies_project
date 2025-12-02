import requests
from typing import Dict, List, Any, Optional
from config import HH_API_URL


class HHAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = HH_API_URL
        self.headers = {'User-Agent': 'HH-User-Agent'}

    def get_employer_info(self, employer_id: str) -> Optional[Dict]:
        """
        Получение информации о работодателе по ID

        Args:
            employer_id (str): ID работодателя на HH.ru

        Returns:
            Optional[Dict]: Информация о работодателе или None при ошибке
        """
        url = f"{self.base_url}employers/{employer_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных о работодателе {employer_id}: {e}")
            return None

    def get_employer_vacancies(self, employer_id: str, per_page: int = 100) -> List[Dict]:
        """
        Получение вакансий работодателя

        Args:
            employer_id (str): ID работодателя
            per_page (int): Количество вакансий на странице

        Returns:
            List[Dict]: Список вакансий
        """
        url = f"{self.base_url}vacancies"
        params = {
            'employer_id': employer_id,
            'per_page': per_page,
            'page': 0,
            'only_with_salary': True
        }

        vacancies = []
        try:
            while True:
                response = requests.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                vacancies.extend(data.get('items', []))

                # Проверяем, есть ли следующая страница
                params['page'] += 1
                if params['page'] >= data.get('pages', 0):
                    break

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий работодателя {employer_id}: {e}")

        return vacancies

    def get_all_employers_data(self, employer_ids: List[str]) -> Dict[str, Any]:
        """
        Получение данных о всех работодателях и их вакансиях

        Args:
            employer_ids (List[str]): Список ID работодателей

        Returns:
            Dict[str, Any]: Словарь с данными о работодателях и вакансиях
        """
        employers_data = {}

        for emp_id in employer_ids:
            print(f"Получение данных о работодателе {emp_id}...")

            # Получаем информацию о работодателе
            employer_info = self.get_employer_info(emp_id)
            if not employer_info:
                continue

            # Получаем вакансии работодателя
            vacancies = self.get_employer_vacancies(emp_id)

            employers_data[emp_id] = {
                'employer': employer_info,
                'vacancies': vacancies
            }

            print(f"Получено {len(vacancies)} вакансий для {employer_info.get('name')}")

        return employers_data