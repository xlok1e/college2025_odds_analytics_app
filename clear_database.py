import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db_manager import DatabaseManager


def clear_all_data():
    print("=" * 80)
    print("ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 80)

    print("\nВНИМАНИЕ: Это удалит ВСЕ данные из базы данных!")
    response = input("Вы уверены? Введите 'yes' для подтверждения: ")

    if response.lower() != 'yes':
        print("Отмена операции")
        return

    print("\n1. Подключение к базе данных...")
    try:
        db = DatabaseManager.from_env()
        db.connect()
        print("✓ Подключение установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return

    print("\n2. Удаление данных...")

    try:
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM odds_records")
            print("✓ Удалены записи коэффициентов")

            cursor.execute("DELETE FROM events")
            print("✓ Удалены события")

            cursor.execute("DELETE FROM bookmakers")
            print("✓ Удалены букмекеры")

            cursor.execute("DELETE FROM bet_types")
            print("✓ Удалены типы ставок")

            cursor.execute("DELETE FROM teams")
            print("✓ Удалены команды")

            cursor.execute("DELETE FROM tournaments")
            print("✓ Удалены турниры")

            cursor.execute("DELETE FROM sports")
            print("✓ Удалены виды спорта")

            cursor.execute("DELETE FROM countries")
            print("✓ Удалены страны")

            cursor.execute("ALTER SEQUENCE odds_records_odds_record_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE events_event_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE bookmakers_bookmaker_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE bet_types_bet_type_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE teams_team_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE tournaments_tournament_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE sports_sport_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE countries_country_id_seq RESTART WITH 1")
            print("✓ Сброшены счетчики ID")

        print("\n✅ База данных успешно очищена!")

    except Exception as e:
        print(f"\nОшибка при очистке: {e}")
    finally:
        db.close()
        print("\nПодключение закрыто")

    print("=" * 80)


if __name__ == "__main__":
    clear_all_data()
