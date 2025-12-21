"""Сервис для получения данных о коэффициентах и статистике из БД"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple


class OddsService:
    """Сервис для работы с данными коэффициентов"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_odds_history(
        self,
        event_id: int,
        bet_type_code: str,
        bookmaker_name: Optional[str] = None,
        bet_parameter: Optional[float] = None
    ) -> List[Dict]:
        """
        Получить историю изменений коэффициента

        Args:
            event_id: ID события
            bet_type_code: Код типа ставки (win_1, draw, win_2, и т.д.)
            bookmaker_name: Название букмекера (если None, то все букмекеры)
            bet_parameter: Параметр ставки (например, 2.5 для тотала)

        Returns:
            Список записей с полями: odds_value, recorded_at, bookmaker_name
        """
        bookmaker_filter = ""
        params = [event_id, bet_type_code]

        if bookmaker_name and bookmaker_name != "Все букмекеры":
            bookmaker_filter = "AND b.bookmaker_name = %s"
            params.append(bookmaker_name)

        if bet_parameter is not None:
            bet_param_filter = "AND orr.bet_parameter = %s"
            params.append(bet_parameter)
        else:
            bet_param_filter = "AND orr.bet_parameter IS NULL"

        query = f"""
            SELECT
                orr.odds_value,
                orr.recorded_at,
                b.bookmaker_name
            FROM odds_records orr
            JOIN bet_types bt ON orr.bet_type_id = bt.bet_type_id
            JOIN bookmakers b ON orr.bookmaker_id = b.bookmaker_id
            WHERE orr.event_id = %s
              AND bt.bet_type_code = %s
              {bookmaker_filter}
              {bet_param_filter}
            ORDER BY orr.recorded_at;
        """

        return self.db.fetch_all(query, tuple(params))

    def get_odds_statistics(
        self,
        event_id: int,
        bet_type_code: str,
        bookmaker_name: Optional[str] = None,
        bet_parameter: Optional[float] = None
    ) -> Dict:
        """
        Получить статистику по коэффициенту

        Returns:
            Dict с полями: min_value, max_value, avg_value, changes_count,
                          min_datetime, max_datetime, first_value, last_value, percent_change
        """
        history = self.get_odds_history(event_id, bet_type_code, bookmaker_name, bet_parameter)

        if not history:
            return {
                'min_value': 0.0,
                'max_value': 0.0,
                'avg_value': 0.0,
                'changes_count': 0,
                'min_datetime': None,
                'max_datetime': None,
                'first_value': 0.0,
                'last_value': 0.0,
                'percent_change': 0.0
            }

        values = [float(record['odds_value']) for record in history]

        min_value = min(values)
        max_value = max(values)
        avg_value = sum(values) / len(values)

        # Найти записи с мин и макс значениями
        min_record = next(r for r in history if float(r['odds_value']) == min_value)
        max_record = next(r for r in history if float(r['odds_value']) == max_value)

        first_value = values[0]
        last_value = values[-1]

        # Процент изменения от первого к последнему
        if first_value > 0:
            percent_change = ((last_value - first_value) / first_value) * 100
        else:
            percent_change = 0.0

        return {
            'min_value': min_value,
            'max_value': max_value,
            'avg_value': avg_value,
            'changes_count': len(history),
            'min_datetime': min_record['recorded_at'],
            'max_datetime': max_record['recorded_at'],
            'first_value': first_value,
            'last_value': last_value,
            'percent_change': percent_change
        }

    def get_chart_data(
        self,
        event_id: int,
        bet_type_code: str,
        bookmaker_name: Optional[str] = None,
        bet_parameter: Optional[float] = None
    ) -> Tuple[List[Tuple[float, float, float]], List[str], List[str]]:
        """
        Получить данные для графика

        Returns:
            Кортеж из трёх элементов:
            - data_points: список точек (x, y, value) для отрисовки
            - time_labels: подписи по оси X (время)
            - value_labels: подписи по оси Y (значения коэффициентов)
        """
        history = self.get_odds_history(event_id, bet_type_code, bookmaker_name, bet_parameter)

        if not history or len(history) < 2:
            # Вернуть пустые данные, если недостаточно записей
            return ([], ["00:00"], ["0.0"])

        values = [float(record['odds_value']) for record in history]
        min_val = min(values)
        max_val = max(values)

        # Добавляем отступы для графика (10% сверху и снизу)
        value_range = max_val - min_val
        if value_range == 0:
            value_range = max_val * 0.1

        chart_min = min_val - value_range * 0.1
        chart_max = max_val + value_range * 0.1
        chart_range = chart_max - chart_min

        # Подготовка точек для графика
        data_points = []
        chart_width = 600  # Виртуальная ширина графика
        chart_height = 200  # Виртуальная высота графика

        for i, record in enumerate(history):
            value = float(record['odds_value'])

            # X координата (равномерно распределяем по ширине)
            x = (i / (len(history) - 1)) * chart_width

            # Y координата (инвертируем, т.к. в графике 0 вверху)
            if chart_range > 0:
                normalized = (value - chart_min) / chart_range
                y = chart_height - (normalized * chart_height)
            else:
                y = chart_height / 2

            data_points.append((x, y, value))

        # Подготовка подписей времени (берём 4-6 равномерных точек)
        num_time_labels = min(6, len(history))
        time_indices = [int(i * (len(history) - 1) / (num_time_labels - 1))
                       for i in range(num_time_labels)]

        time_labels = []
        for idx in time_indices:
            dt = history[idx]['recorded_at']
            if isinstance(dt, datetime):
                time_labels.append(dt.strftime('%H:%M'))
            else:
                time_labels.append(str(dt)[:5])

        # Подготовка подписей значений (5 уровней)
        value_labels = []
        for i in range(5):
            value = chart_max - (i * chart_range / 4)
            value_labels.append(f"{value:.2f}")

        return (data_points, time_labels, value_labels)

    def detect_sharp_changes(
        self,
        event_id: int,
        bet_type_code: str,
        bookmaker_name: Optional[str] = None,
        bet_parameter: Optional[float] = None,
        threshold_percent: float = 10.0,
        time_window_minutes: int = 60
    ) -> List[Dict]:
        """
        Обнаружить резкие изменения коэффициентов

        Args:
            threshold_percent: Порог изменения в процентах (по умолчанию 10%)
            time_window_minutes: Временное окно в минутах (по умолчанию 60 минут)

        Returns:
            Список изменений с полями: datetime, old_value, new_value,
                                      percent_change, minutes_elapsed
        """
        history = self.get_odds_history(event_id, bet_type_code, bookmaker_name, bet_parameter)

        if len(history) < 2:
            return []

        sharp_changes = []

        for i in range(1, len(history)):
            prev_record = history[i - 1]
            curr_record = history[i]

            prev_value = float(prev_record['odds_value'])
            curr_value = float(curr_record['odds_value'])

            # Вычисляем процент изменения
            if prev_value > 0:
                percent_change = abs((curr_value - prev_value) / prev_value) * 100
            else:
                continue

            # Вычисляем разницу во времени
            prev_time = prev_record['recorded_at']
            curr_time = curr_record['recorded_at']

            if isinstance(prev_time, datetime) and isinstance(curr_time, datetime):
                time_diff = (curr_time - prev_time).total_seconds() / 60  # в минутах
            else:
                time_diff = 0

            # Проверяем условия резкого изменения
            if percent_change >= threshold_percent and time_diff <= time_window_minutes:
                change_type = "рост" if curr_value > prev_value else "падение"

                sharp_changes.append({
                    'datetime': curr_time,
                    'old_value': prev_value,
                    'new_value': curr_value,
                    'percent_change': percent_change,
                    'minutes_elapsed': int(time_diff),
                    'change_type': change_type
                })

        return sharp_changes

    def get_bet_type_code(self, bet_type_name: str) -> str:
        """Преобразовать название типа ставки в код"""
        mapping = {
            'П1': 'win_1',
            'X': 'draw',
            'П2': 'win_2',
            'Тотал больше 2.5': 'total_over',
            'Тотал меньше 2.5': 'total_under',
            'Фора 1': 'handicap_1',
            'Фора 2': 'handicap_2'
        }
        return mapping.get(bet_type_name, 'win_1')

    def get_bet_parameter(self, bet_type_name: str) -> Optional[float]:
        """Извлечь параметр из названия типа ставки"""
        if 'Тотал' in bet_type_name and '2.5' in bet_type_name:
            return 2.5
        return None
