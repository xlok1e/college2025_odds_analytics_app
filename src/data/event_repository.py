from typing import List, Optional

from src.models.event import Coefficients, Event


class EventRepository:
    """Репозиторий для работы с событиями из базы данных"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_all_events(self) -> List[Event]:
        """Получить все события из базы данных"""
        events_data = self.db.get_all_events()
        events = []

        for event_data in events_data:
            # Получаем букмекеров для события
            bookmakers = self.db.get_event_bookmakers(event_data['event_id'])

            # Получаем последние коэффициенты
            coefficients_data = self.db.get_latest_coefficients(event_data['event_id'])

            # Форматируем дату
            event_datetime = event_data['event_datetime']
            formatted_date = event_datetime.strftime('%d.%m.%Y %H:%M')

            # Создаем объект Event
            event = Event(
                id=event_data['event_id'],
                sport=event_data['sport_name'],
                tournament=event_data['tournament_name'],
                country=event_data['country_name'],
                team1=event_data['team1_name'],
                team2=event_data['team2_name'],
                date=formatted_date,
                records_count=event_data['records_count'],
                bookmakers=bookmakers,
                coefficients=Coefficients(
                    p1=coefficients_data.get('p1', 0.0),
                    x=coefficients_data.get('x', 0.0),
                    p2=coefficients_data.get('p2', 0.0)
                )
            )
            events.append(event)

        return events

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Получить событие по ID"""
        events = self.get_all_events()
        return next((e for e in events if e.id == event_id), None)

    def delete_event(self, event_id: int) -> bool:
        """Удалить событие по ID"""
        try:
            query = "DELETE FROM events WHERE event_id = %s"
            self.db.execute_query(query, (event_id,))
            return True
        except Exception as e:
            print(f"✗ Ошибка удаления события: {e}")
            return False
