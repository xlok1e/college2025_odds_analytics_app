"""Моковые данные для тестирования"""

from src.models.event import Event, Coefficients


MOCK_EVENTS = [
    Event(
        id=1,
        sport="Футбол",
        tournament="Российская Премьер-Лига",
        country="Россия",
        team1="Зенит",
        team2="Спартак",
        date="15.03.2025 19:00",
        records_count=156,
        bookmakers=["1xBet", "Фонбет", "Лига Ставок"],
        coefficients=Coefficients(p1=2.1, x=3.4, p2=3.8)
    ),
    Event(
        id=2,
        sport="Футбол",
        tournament="Лига Чемпионов",
        country="Европа",
        team1="Реал Мадрид",
        team2="Манчестер Сити",
        date="16.03.2025 22:00",
        records_count=243,
        bookmakers=["1xBet", "Фонбет", "Лига Ставок", "Winline"],
        coefficients=Coefficients(p1=2.45, x=3.2, p2=3.1)
    ),
    Event(
        id=3,
        sport="Хоккей",
        tournament="КХЛ",
        country="Россия",
        team1="ЦСКА",
        team2="СКА",
        date="17.03.2025 17:30",
        records_count=89,
        bookmakers=["1xBet", "Фонбет"],
        coefficients=Coefficients(p1=2.65, x=4.1, p2=2.55)
    ),
    Event(
        id=4,
        sport="Баскетбол",
        tournament="Единая лига ВТБ",
        country="Россия",
        team1="ЦСКА",
        team2="Зенит",
        date="18.03.2025 18:00",
        records_count=67,
        bookmakers=["1xBet", "Лига Ставок"],
        coefficients=Coefficients(p1=1.85, x=15.0, p2=2.05)
    ),
    Event(
        id=5,
        sport="Футбол",
        tournament="Английская Премьер-Лига",
        country="Англия",
        team1="Ливерпуль",
        team2="Арсенал",
        date="19.03.2025 20:00",
        records_count=198,
        bookmakers=["1xBet", "Фонбет", "Лига Ставок", "Winline"],
        coefficients=Coefficients(p1=2.2, x=3.5, p2=3.4)
    ),
    Event(
        id=6,
        sport="Теннис",
        tournament="ATP Masters",
        country="США",
        team1="Медведев Д.",
        team2="Алькарас К.",
        date="20.03.2025 21:00",
        records_count=134,
        bookmakers=["1xBet", "Фонбет"],
        coefficients=Coefficients(p1=1.95, x=0, p2=1.9)
    ),
]
