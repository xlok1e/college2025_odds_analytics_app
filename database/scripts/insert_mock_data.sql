-- Заполнение таблицы стран
INSERT INTO countries (country_name, country_code) VALUES
('Россия', 'RUS'),
('Англия', 'ENG'),
('Испания', 'ESP'),
('Германия', 'GER'),
('Италия', 'ITA'),
('Франция', 'FRA'),
('США', 'USA'),
('Европа', 'EUR')
ON CONFLICT (country_code) DO NOTHING;

-- Заполнение таблицы видов спорта
INSERT INTO sports (sport_name) VALUES
('Футбол'),
('Хоккей'),
('Баскетбол'),
('Теннис')
ON CONFLICT (sport_name) DO NOTHING;

-- Заполнение таблицы команд
INSERT INTO teams (team_name, sport_id, country_id) VALUES
-- Футбольные команды России
('Зенит', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Спартак', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('ЦСКА', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
-- Футбольные команды Европы
('Реал Мадрид', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ESP')),
('Манчестер Сити', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ENG')),
('Ливерпуль', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ENG')),
('Арсенал', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ENG')),
-- Хоккейные команды
('ЦСКА', (SELECT sport_id FROM sports WHERE sport_name = 'Хоккей'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('СКА', (SELECT sport_id FROM sports WHERE sport_name = 'Хоккей'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
-- Баскетбольные команды
('ЦСКА', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Зенит', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
-- Теннисисты
('Медведев Д.', (SELECT sport_id FROM sports WHERE sport_name = 'Теннис'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Алькарас К.', (SELECT sport_id FROM sports WHERE sport_name = 'Теннис'), (SELECT country_id FROM countries WHERE country_code = 'ESP'));

-- Заполнение таблицы турниров
INSERT INTO tournaments (tournament_name, sport_id, country_id) VALUES
('Российская Премьер-Лига', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Лига Чемпионов', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'EUR')),
('Английская Премьер-Лига', (SELECT sport_id FROM sports WHERE sport_name = 'Футбол'), (SELECT country_id FROM countries WHERE country_code = 'ENG')),
('КХЛ', (SELECT sport_id FROM sports WHERE sport_name = 'Хоккей'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('Единая лига ВТБ', (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол'), (SELECT country_id FROM countries WHERE country_code = 'RUS')),
('ATP Masters', (SELECT sport_id FROM sports WHERE sport_name = 'Теннис'), (SELECT country_id FROM countries WHERE country_code = 'USA'));

-- Заполнение таблицы букмекеров
INSERT INTO bookmakers (bookmaker_name) VALUES
('1xBet'),
('Фонбет'),
('Лига Ставок'),
('Winline')
ON CONFLICT (bookmaker_name) DO NOTHING;

-- Заполнение таблицы типов ставок
INSERT INTO bet_types (bet_type_code, bet_type_name, has_parameter) VALUES
('win_1', 'П1', FALSE),
('draw', 'X', FALSE),
('win_2', 'П2', FALSE),
('total_over', 'Тотал больше', TRUE),
('total_under', 'Тотал меньше', TRUE),
('handicap_1', 'Фора 1', TRUE),
('handicap_2', 'Фора 2', TRUE)
ON CONFLICT (bet_type_code) DO NOTHING;

-- Заполнение таблицы событий
INSERT INTO events (team1_id, team2_id, tournament_id, event_datetime) VALUES
-- Зенит - Спартак
(
    (SELECT team_id FROM teams WHERE team_name = 'Зенит' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Футбол')),
    (SELECT team_id FROM teams WHERE team_name = 'Спартак' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Футбол')),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Российская Премьер-Лига'),
    '2025-03-15 19:00:00'
),
-- Реал Мадрид - Манчестер Сити
(
    (SELECT team_id FROM teams WHERE team_name = 'Реал Мадрид'),
    (SELECT team_id FROM teams WHERE team_name = 'Манчестер Сити'),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Лига Чемпионов'),
    '2025-03-16 22:00:00'
),
-- ЦСКА - СКА (Хоккей)
(
    (SELECT team_id FROM teams WHERE team_name = 'ЦСКА' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Хоккей')),
    (SELECT team_id FROM teams WHERE team_name = 'СКА'),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'КХЛ'),
    '2025-03-17 17:30:00'
),
-- ЦСКА - Зенит (Баскетбол)
(
    (SELECT team_id FROM teams WHERE team_name = 'ЦСКА' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол')),
    (SELECT team_id FROM teams WHERE team_name = 'Зенит' AND sport_id = (SELECT sport_id FROM sports WHERE sport_name = 'Баскетбол')),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Единая лига ВТБ'),
    '2025-03-18 18:00:00'
),
-- Ливерпуль - Арсенал
(
    (SELECT team_id FROM teams WHERE team_name = 'Ливерпуль'),
    (SELECT team_id FROM teams WHERE team_name = 'Арсенал'),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'Английская Премьер-Лига'),
    '2025-03-19 20:00:00'
),
-- Медведев - Алькарас (Теннис)
(
    (SELECT team_id FROM teams WHERE team_name = 'Медведев Д.'),
    (SELECT team_id FROM teams WHERE team_name = 'Алькарас К.'),
    (SELECT tournament_id FROM tournaments WHERE tournament_name = 'ATP Masters'),
    '2025-03-20 21:00:00'
);

-- Заполнение таблицы коэффициентов для события 1 (Зенит - Спартак)
-- Текущие коэффициенты
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- 1xBet
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.10, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.40, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.80, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_over'), 2.5, 1.95, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'total_under'), 2.5, 1.85, '2025-03-15 18:00:00'),
-- Фонбет
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.08, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.35, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.75, '2025-03-15 18:00:00'),
-- Лига Ставок
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.12, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.38, '2025-03-15 18:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.82, '2025-03-15 18:00:00');

-- История изменений коэффициентов для графика (П1 от 1xBet)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.25, '2025-03-15 10:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.30, '2025-03-15 11:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.15, '2025-03-15 12:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.84, '2025-03-15 14:23:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.90, '2025-03-15 15:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.05, '2025-03-15 16:00:00'),
(1, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.95, '2025-03-15 17:00:00');

-- Заполнение коэффициентов для события 2 (Реал Мадрид - Манчестер Сити)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
-- 1xBet
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.45, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.20, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.10, '2025-03-16 20:00:00'),
-- Фонбет
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.42, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.18, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.08, '2025-03-16 20:00:00'),
-- Лига Ставок
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.48, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.22, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.12, '2025-03-16 20:00:00'),
-- Winline
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.44, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.19, '2025-03-16 20:00:00'),
(2, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.09, '2025-03-16 20:00:00');

-- Заполнение коэффициентов для события 3 (ЦСКА - СКА Хоккей)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.65, '2025-03-17 16:00:00'),
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 4.10, '2025-03-17 16:00:00'),
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.55, '2025-03-17 16:00:00'),
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.62, '2025-03-17 16:00:00'),
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 4.05, '2025-03-17 16:00:00'),
(3, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.52, '2025-03-17 16:00:00');

-- Заполнение коэффициентов для события 4 (ЦСКА - Зенит Баскетбол)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.85, '2025-03-18 17:00:00'),
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 15.00, '2025-03-18 17:00:00'),
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.05, '2025-03-18 17:00:00'),
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.82, '2025-03-18 17:00:00'),
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 14.50, '2025-03-18 17:00:00'),
(4, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 2.08, '2025-03-18 17:00:00');

-- Заполнение коэффициентов для события 5 (Ливерпуль - Арсенал)
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.20, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.50, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.40, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.18, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.48, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.38, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.22, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.52, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Лига Ставок'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.42, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 2.19, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'draw'), NULL, 3.49, '2025-03-19 19:00:00'),
(5, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Winline'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 3.39, '2025-03-19 19:00:00');

-- Заполнение коэффициентов для события 6 (Медведев - Алькарас Теннис)
-- В теннисе нет ничьей
INSERT INTO odds_records (event_id, bookmaker_id, bet_type_id, bet_parameter, odds_value, recorded_at) VALUES
(6, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.95, '2025-03-20 20:00:00'),
(6, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = '1xBet'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.90, '2025-03-20 20:00:00'),
(6, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_1'), NULL, 1.93, '2025-03-20 20:00:00'),
(6, (SELECT bookmaker_id FROM bookmakers WHERE bookmaker_name = 'Фонбет'), (SELECT bet_type_id FROM bet_types WHERE bet_type_code = 'win_2'), NULL, 1.88, '2025-03-20 20:00:00');
