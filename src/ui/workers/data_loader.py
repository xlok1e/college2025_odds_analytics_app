from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QThread, Signal


class EventLoader(QObject):
    """Worker для загрузки события в отдельном потоке"""

    finished = Signal(object)  # Event object
    error = Signal(str)

    def __init__(self, event_repository, event_id: int):
        super().__init__()
        self.event_repository = event_repository
        self.event_id = event_id

    def run(self):
        """Загрузка события"""
        try:
            event = self.event_repository.get_event_by_id(self.event_id)
            self.finished.emit(event)
        except Exception as e:
            self.error.emit(str(e))


class ChartDataLoader(QObject):
    """Worker для загрузки данных графика в отдельном потоке"""

    finished = Signal(list, list, list)  # data_points, time_labels, value_labels
    error = Signal(str)

    def __init__(self, odds_service, event_id: int, bet_type: str, bookmaker: str):
        super().__init__()
        self.odds_service = odds_service
        self.event_id = event_id
        self.bet_type = bet_type
        self.bookmaker = bookmaker

    def run(self):
        """Загрузка данных графика"""
        try:
            bet_type_code = self.odds_service.get_bet_type_code(self.bet_type)
            bet_parameter = self.odds_service.get_bet_parameter(self.bet_type)

            bookmaker = None if self.bookmaker == "Все букмекеры" else self.bookmaker

            data_points, time_labels, value_labels = self.odds_service.get_chart_data(
                self.event_id,
                bet_type_code,
                bookmaker,
                bet_parameter
            )

            self.finished.emit(data_points, time_labels, value_labels)

        except Exception as e:
            self.error.emit(str(e))


class StatisticsDataLoader(QObject):
    """Worker для загрузки статистики в отдельном потоке"""

    finished = Signal(dict)  # statistics_data
    error = Signal(str)

    def __init__(self, odds_service, event_id: int, bet_type: str):
        super().__init__()
        self.odds_service = odds_service
        self.event_id = event_id
        self.bet_type = bet_type

    def run(self):
        """Загрузка статистики"""
        try:
            bet_type_code = self.odds_service.get_bet_type_code(self.bet_type)
            bet_parameter = self.odds_service.get_bet_parameter(self.bet_type)

            statistics = self.odds_service.get_odds_statistics(
                self.event_id,
                bet_type_code,
                None,  # bookmaker_filter
                bet_parameter
            )

            self.finished.emit(statistics)

        except Exception as e:
            self.error.emit(str(e))


class EventDetailDataLoader(QObject):
    """Worker для загрузки всех данных детального просмотра события"""

    chart_data_loaded = Signal(list, list, list)  # data_points, time_labels, value_labels
    statistics_loaded = Signal(dict)  # statistics_data
    all_finished = Signal()
    error = Signal(str)

    def __init__(self, odds_service, event_id: int, bet_type: str, bookmaker: str):
        super().__init__()
        self.odds_service = odds_service
        self.event_id = event_id
        self.bet_type = bet_type
        self.bookmaker = bookmaker

    def run(self):
        """Загрузка всех данных параллельно"""
        try:
            # Загрузка данных графика
            bet_type_code = self.odds_service.get_bet_type_code(self.bet_type)
            bet_parameter = self.odds_service.get_bet_parameter(self.bet_type)

            bookmaker = None if self.bookmaker == "Все букмекеры" else self.bookmaker

            data_points, time_labels, value_labels = self.odds_service.get_chart_data(
                self.event_id,
                bet_type_code,
                bookmaker,
                bet_parameter
            )

            self.chart_data_loaded.emit(data_points, time_labels, value_labels)

            # Загрузка статистики
            statistics = self.odds_service.get_odds_statistics(
                self.event_id,
                bet_type_code,
                None,  # bookmaker_filter
                bet_parameter
            )

            self.statistics_loaded.emit(statistics)

            self.all_finished.emit()

        except Exception as e:
            self.error.emit(str(e))


__all__ = ['EventLoader', 'ChartDataLoader', 'StatisticsDataLoader', 'EventDetailDataLoader']
