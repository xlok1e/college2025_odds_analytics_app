-- Очистка существующих данных
TRUNCATE TABLE odds_records, events, tournaments, teams, bookmakers, bet_types, sports, countries RESTART IDENTITY CASCADE;

-- ========================================
-- СПРАВОЧНИКИ
-- ========================================

-- Страны
INSERT INTO countries (country_name, country_code) VALUES
('Россия', 'RUS'),
('Испания', 'ESP'),
('Англия', 'ENG')
ON CONFLICT (country_code) DO NOTHING;

-- Виды спорта
INSERT INTO sports (sport_name) VALUES
('Футбол'),
('Баскетбол')
ON CONFLICT (sport_name) DO NOTHING;

-- Букмекеры
INSERT INTO bookmakers (bookmaker_name) VALUES
('1xBet'),
('Фонбет'),
('Лига Ставок'),
('Winline'),
('Бетсити'),
('Мелбет'),
('Пари'),
('Олимп')
ON CONFLICT (bookmaker_name) DO NOTHING;

-- Типы ставок
INSERT INTO bet_types (bet_type_code, bet_type_name, has_parameter) VALUES
-- Основные исходы
('win_1', 'П1', FALSE),
('draw', 'X', FALSE),
('win_2', 'П2', FALSE),
-- Двойной шанс
('1x', '1X', FALSE),
('12', '12', FALSE),
('x2', 'X2', FALSE),
-- Тоталы
('total_over', 'Тотал больше', TRUE),
('total_under', 'Тотал меньше', TRUE),
('total_1_over', 'Тотал 1 больше', TRUE),
('total_1_under', 'Тотал 1 меньше', TRUE),
('total_2_over', 'Тотал 2 больше', TRUE),
('total_2_under', 'Тотал 2 меньше', TRUE),
-- Форы
('handicap_1', 'Фора 1', TRUE),
('handicap_2', 'Фора 2', TRUE),
-- Обе забьют
('both_score_yes', 'Обе забьют - Да', FALSE),
('both_score_no', 'Обе забьют - Нет', FALSE),
-- Индивидуальный тотал
('individual_total_1_over', 'ИТ1 больше', TRUE),
('individual_total_1_under', 'ИТ1 меньше', TRUE),
('individual_total_2_over', 'ИТ2 больше', TRUE),
('individual_total_2_under', 'ИТ2 меньше', TRUE),
-- Точный счет (примеры)
('exact_score', 'Точный счет', FALSE),
-- Первый гол
('first_goal_1', 'Первый гол 1', FALSE),
('first_goal_2', 'Первый гол 2', FALSE),
('no_goals', 'Не забьет никто', FALSE)
ON CONFLICT (bet_type_code) DO NOTHING;

-- ========================================
-- СОБЫТИЕ 1: Реал Мадрид - Барселона
-- ========================================

-- Команды
INSERT INTO teams (team_name, sport_id, country_id) VALUES
('Реал Мадрид', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ESP')),
('Барселона', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ESP'));

-- Турнир
INSERT INTO tournaments (tournament_name, sport_id, country_id) VALUES
('Ла Лига', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ESP'));

-- Событие
INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime) VALUES
(
    (SELECT team_id FROM teams WHERE team_name = 'Реал Мадрид'),
    (SELECT team_id FROM teams WHERE team_name = 'Барселона'),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Ла Лига'),
    '2025-03-28 21:00:00'
);

-- ========================================
-- КОЭФФИЦИЕНТЫ ДЛЯ СОБЫТИЯ 1
-- ========================================

-- История изменений коэффициентов за последние 7 дней
-- День -7 (21.03.2025 10:00) - первые котировки

-- 1xBet
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- Основные исходы
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.15, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.60, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.35, '2025-03-21 10:00:00'),
-- Двойной шанс
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = '1x'), NULL, 1.32, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = '12'), NULL, 1.26, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'x2'), NULL, 1.68, '2025-03-21 10:00:00'),
-- Тоталы
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.70, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.18, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 3.5, 2.65, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 3.5, 1.48, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 1.5, 1.18, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 1.5, 5.20, '2025-03-21 10:00:00'),
-- Обе забьют
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_yes'), NULL, 1.58, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_no'), NULL, 2.40, '2025-03-21 10:00:00'),
-- Форы
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -1.0, 3.45, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 1.0, 1.32, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), 0.0, 1.85, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 0.0, 2.05, '2025-03-21 10:00:00'),
-- Индивидуальные тоталы
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_over'), 1.5, 1.48, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_under'), 1.5, 2.65, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_over'), 1.5, 1.72, '2025-03-21 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_under'), 1.5, 2.15, '2025-03-21 10:00:00');

-- Фонбет
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.12, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.65, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.40, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.68, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.22, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_yes'), NULL, 1.60, '2025-03-21 10:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_no'), NULL, 2.38, '2025-03-21 10:15:00');

-- Лига Ставок
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.18, '2025-03-21 10:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.55, '2025-03-21 10:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.32, '2025-03-21 10:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.72, '2025-03-21 10:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.16, '2025-03-21 10:30:00');

-- Winline
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.14, '2025-03-21 11:00:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.58, '2025-03-21 11:00:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.38, '2025-03-21 11:00:00');

-- День -6 (22.03.2025) - небольшие изменения
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.18, '2025-03-22 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.55, '2025-03-22 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.30, '2025-03-22 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.72, '2025-03-22 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.15, '2025-03-22 14:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.16, '2025-03-22 14:30:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.58, '2025-03-22 14:30:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.35, '2025-03-22 14:30:00');

-- День -5 (23.03.2025) - стабильно
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.20, '2025-03-23 16:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.50, '2025-03-23 16:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.28, '2025-03-23 16:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_yes'), NULL, 1.62, '2025-03-23 16:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_no'), NULL, 2.35, '2025-03-23 16:00:00');

-- День -4 (24.03.2025) - легкое движение к Реалу
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.08, '2025-03-24 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.60, '2025-03-24 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.50, '2025-03-24 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.75, '2025-03-24 10:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.10, '2025-03-24 10:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.10, '2025-03-24 10:45:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.58, '2025-03-24 10:45:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.48, '2025-03-24 10:45:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.12, '2025-03-24 11:00:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.55, '2025-03-24 11:00:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.45, '2025-03-24 11:00:00');

-- День -3 (25.03.2025) - продолжение тренда
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.05, '2025-03-25 12:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.65, '2025-03-25 12:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.58, '2025-03-25 12:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), 0.0, 1.80, '2025-03-25 12:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 0.0, 2.12, '2025-03-25 12:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.06, '2025-03-25 13:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.62, '2025-03-25 13:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.55, '2025-03-25 13:00:00');

-- День -2 (26.03.2025) - новости о травме игрока Барселоны - резкое изменение!
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.88, '2025-03-26 15:30:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.80, '2025-03-26 15:30:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.10, '2025-03-26 15:30:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.80, '2025-03-26 15:30:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.05, '2025-03-26 15:30:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.90, '2025-03-26 15:45:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.75, '2025-03-26 15:45:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.05, '2025-03-26 15:45:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.92, '2025-03-26 16:00:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.72, '2025-03-26 16:00:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.00, '2025-03-26 16:00:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.89, '2025-03-26 16:15:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.78, '2025-03-26 16:15:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.08, '2025-03-26 16:15:00');

-- День -1 (27.03.2025) - активная торговля перед матчем
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- Утро
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.90, '2025-03-27 09:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.75, '2025-03-27 09:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.05, '2025-03-27 09:00:00'),
-- День
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.92, '2025-03-27 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.72, '2025-03-27 14:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 4.00, '2025-03-27 14:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.93, '2025-03-27 14:30:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.70, '2025-03-27 14:30:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.98, '2025-03-27 14:30:00'),
-- Вечер (финальные котировки)
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.95, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.68, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.95, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.82, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.02, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 3.5, 2.75, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 3.5, 1.45, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_yes'), NULL, 1.65, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_no'), NULL, 2.28, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -1.0, 3.60, '2025-03-27 20:00:00'),
(1, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 1.0, 1.30, '2025-03-27 20:00:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.94, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.70, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.98, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.80, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.05, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_yes'), NULL, 1.63, '2025-03-27 20:15:00'),
(1, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'both_score_no'), NULL, 2.32, '2025-03-27 20:15:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.96, '2025-03-27 20:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.65, '2025-03-27 20:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.92, '2025-03-27 20:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.83, '2025-03-27 20:30:00'),
(1, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 2.00, '2025-03-27 20:30:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.93, '2025-03-27 20:45:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.72, '2025-03-27 20:45:00'),
(1, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.98, '2025-03-27 20:45:00');

-- ========================================
-- СОБЫТИЕ 2: ЦСКА - Зенит (Баскетбол)
-- ========================================

-- Команды
INSERT INTO teams (team_name, sport_id, country_id) VALUES
('ЦСКА', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Зенит', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS'));

-- Турнир
INSERT INTO tournaments (tournament_name, sport_id, country_id) VALUES
('Единая лига ВТБ', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS'));

-- Событие
INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime) VALUES
(
    (SELECT team_id FROM teams WHERE team_name = 'ЦСКА' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол')),
    (SELECT team_id FROM teams WHERE team_name = 'Зенит' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол')),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Единая лига ВТБ'),
    '2025-03-30 18:00:00'
);

-- ========================================
-- КОЭФФИЦИЕНТЫ ДЛЯ СОБЫТИЯ 2
-- ========================================

-- В баскетболе нет ничьей, только П1 и П2
-- История за последние 5 дней

-- День -5 (25.03.2025)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- 1xBet
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.65, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.28, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 165.5, 1.90, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 165.5, 1.90, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 170.5, 2.15, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 170.5, 1.70, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 160.5, 1.65, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 160.5, 2.20, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -5.5, 1.90, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 5.5, 1.90, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -8.5, 2.15, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 8.5, 1.70, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_over'), 85.5, 1.85, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_under'), 85.5, 1.95, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_over'), 80.5, 1.95, '2025-03-25 12:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_under'), 80.5, 1.85, '2025-03-25 12:00:00'),
-- Фонбет
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.63, '2025-03-25 12:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.32, '2025-03-25 12:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 165.5, 1.88, '2025-03-25 12:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 165.5, 1.92, '2025-03-25 12:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -5.5, 1.88, '2025-03-25 12:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 5.5, 1.92, '2025-03-25 12:30:00'),
-- Лига Ставок
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.67, '2025-03-25 13:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.25, '2025-03-25 13:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 165.5, 1.92, '2025-03-25 13:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 165.5, 1.88, '2025-03-25 13:00:00');

-- День -4 (26.03.2025)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.68, '2025-03-26 14:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.22, '2025-03-26 14:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 165.5, 1.92, '2025-03-26 14:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 165.5, 1.88, '2025-03-26 14:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -5.5, 1.92, '2025-03-26 14:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 5.5, 1.88, '2025-03-26 14:00:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.66, '2025-03-26 14:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.26, '2025-03-26 14:30:00');

-- День -3 (27.03.2025)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.70, '2025-03-27 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.18, '2025-03-27 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 166.5, 1.90, '2025-03-27 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 166.5, 1.90, '2025-03-27 10:00:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.69, '2025-03-27 10:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.20, '2025-03-27 10:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.72, '2025-03-27 11:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.15, '2025-03-27 11:00:00');

-- День -2 (28.03.2025) - резкое изменение после новостей о травме лидера ЦСКА
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.85, '2025-03-28 16:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.95, '2025-03-28 16:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 166.5, 1.88, '2025-03-28 16:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 166.5, 1.92, '2025-03-28 16:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -5.5, 2.20, '2025-03-28 16:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 5.5, 1.65, '2025-03-28 16:00:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.88, '2025-03-28 16:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.92, '2025-03-28 16:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 166.5, 1.90, '2025-03-28 16:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 166.5, 1.90, '2025-03-28 16:15:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.86, '2025-03-28 16:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.94, '2025-03-28 16:30:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.87, '2025-03-28 16:45:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.93, '2025-03-28 16:45:00');

-- День -1 (29.03.2025) - день перед матчем
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- Утро
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.83, '2025-03-29 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.97, '2025-03-29 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.90, '2025-03-29 10:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.90, '2025-03-29 10:00:00'),
-- День
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.85, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.95, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.88, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.92, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -3.5, 1.90, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 3.5, 1.90, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_over'), 82.5, 1.90, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_under'), 82.5, 1.90, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_over'), 82.5, 1.90, '2025-03-29 15:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_under'), 82.5, 1.90, '2025-03-29 15:00:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.84, '2025-03-29 15:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.96, '2025-03-29 15:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.90, '2025-03-29 15:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.90, '2025-03-29 15:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -3.5, 1.88, '2025-03-29 15:30:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 3.5, 1.92, '2025-03-29 15:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.86, '2025-03-29 16:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.94, '2025-03-29 16:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.92, '2025-03-29 16:00:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.88, '2025-03-29 16:00:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.85, '2025-03-29 16:15:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.95, '2025-03-29 16:15:00'),
-- Вечер (финальные котировки)
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.87, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.93, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.85, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.95, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 169.5, 2.10, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 169.5, 1.75, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 159.5, 1.60, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 159.5, 2.35, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -3.5, 1.88, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 3.5, 1.92, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -6.5, 2.15, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 6.5, 1.70, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_over'), 82.5, 1.88, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_1_under'), 82.5, 1.92, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_over'), 82.5, 1.92, '2025-03-29 21:00:00'),
(2, 1, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'individual_total_2_under'), 82.5, 1.88, '2025-03-29 21:00:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.86, '2025-03-29 21:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.94, '2025-03-29 21:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.87, '2025-03-29 21:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.93, '2025-03-29 21:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_1'), -3.5, 1.90, '2025-03-29 21:15:00'),
(2, 2, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'handicap_2'), 3.5, 1.90, '2025-03-29 21:15:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.88, '2025-03-29 21:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.92, '2025-03-29 21:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 164.5, 1.90, '2025-03-29 21:30:00'),
(2, 3, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 164.5, 1.90, '2025-03-29 21:30:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.87, '2025-03-29 21:45:00'),
(2, 4, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.93, '2025-03-29 21:45:00');

-- Добавляем больше букмекеров
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- Бетсити
(1, 5, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.94, '2025-03-27 20:00:00'),
(1, 5, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.71, '2025-03-27 20:00:00'),
(1, 5, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.97, '2025-03-27 20:00:00'),
(2, 5, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.85, '2025-03-29 21:00:00'),
(2, 5, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.95, '2025-03-29 21:00:00'),
-- Мелбет
(1, 6, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.96, '2025-03-27 20:00:00'),
(1, 6, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.67, '2025-03-27 20:00:00'),
(1, 6, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.93, '2025-03-27 20:00:00'),
(2, 6, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.86, '2025-03-29 21:00:00'),
(2, 6, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.94, '2025-03-29 21:00:00'),
-- Пари
(1, 7, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.93, '2025-03-27 20:00:00'),
(1, 7, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.73, '2025-03-27 20:00:00'),
(1, 7, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.99, '2025-03-27 20:00:00'),
(2, 7, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.84, '2025-03-29 21:00:00'),
(2, 7, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.96, '2025-03-29 21:00:00'),
-- Олимп
(1, 8, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.97, '2025-03-27 20:00:00'),
(1, 8, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.65, '2025-03-27 20:00:00'),
(1, 8, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.90, '2025-03-27 20:00:00'),
(2, 8, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.88, '2025-03-29 21:00:00'),
(2, 8, (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.92, '2025-03-29 21:00:00');
