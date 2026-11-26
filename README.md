# PUBG Match Tracker

## Опис проєкту
Програма для обліку та аналізу матчів у PUBG.

## Для кого
Для гравців PUBG, які хочуть відстежувати свою статистику.

## Дані матчу
- Дата матчу
- Результат
- Кількість вбивств
- Тривалість матчу
- Коментар

## Функціонал
- Додавання матчу
- Перегляд усіх матчів
- Пошук матчів
- Формування статистичного звіту

## Технології
Python, Git, GitHub.

## Запуск програми
python cli.py
## Приклади команд

- python cli.py add 2026-11-26 win 5 20 "First match"
- python cli.py list
- python cli.py find win
- python cli.py report
- python tests.py

## Формат даних

Дані зберігаються у текстовому файлі matches.txt у форматі JSON.
Тривалість матчу вимірюється у хвилинах.
Результат матчу: win або loss.
## Лабораторна робота №7

Вебсервіс PUBG Match Tracker на Flask.

## Встановлення залежностей

pip install -r requirements.txt

## Запуск вебсервісу

python app.py

Адреса сервера: http://127.0.0.1:5000

## HTTP API

| Метод | Маршрут | Призначення |
|---|---|---|
| GET | /matches | Перегляд усіх матчів |
| GET | /matches?result=win | Пошук перемог |
| POST | /matches | Додавання матчу |
| DELETE | /matches/2 | Видалення матчу |
| GET | /report | Статистичний звіт |

## База даних

SQLite, файл matches.db.

Поля: id, date, result, kills, duration, note.

Починаючи з лабораторної №7, дані зберігаються
у SQLite замість текстового файлу.

## Перевірка

curl http://127.0.0.1:5000/matches

curl "http://127.0.0.1:5000/matches?result=win"

curl http://127.0.0.1:5000/report

curl -X POST http://127.0.0.1:5000/matches -H "Content-Type: application/json" -d '{"date":"2026-11-26","result":"win","kills":5,"duration":20}'

curl -X DELETE http://127.0.0.1:5000/matches/2

Некоректний запит повертає HTTP 400.
Відсутній запис повертає HTTP 404.
## Запуск сервера

Команди виконуються з кореневої папки проєкту
PUBG-Match-Tracker в активованому середовищі venv.

1. Запуск сервера Waitress:

```bash
waitress-serve --listen=127.0.0.1:8000 app:app
```

2. Запуск тимчасового тунелю Cloudflare в іншому терміналі:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

API доступний за маршрутом /matches.

Публічний доступ перевірено з комп'ютера та телефона.
Також перевірено обмеження доступу через локальну мережу.

Після завершення роботи сервер і тунель
необхідно зупинити через Ctrl+C.

## Запуск сервера

### Docker

docker compose up -d --build

docker compose logs -f

docker compose down

База даних зберігається у директорії data.
Змінні середовища зберігаються у файлі .env.

### Cloudflare Tunnel

Постійний тунель забезпечує HTTPS-доступ до API.

- Frontend: https://pubgmatchtracker.pp.ua
- API: https://api.pubgmatchtracker.pp.ua
- Health: https://api.pubgmatchtracker.pp.ua/health

### CI/CD

GitHub Actions автоматично запускає pytest
та збирає Docker-образ після push у master.

Self-hosted runner передбачений для автоматичного
розгортання, але поки не налаштований.

### Моніторинг

UptimeRobot перевіряє /health кожні 5 хвилин.

### Поточний стан

Docker Desktop встановлено, але запуск заблоковано
через проблему Virtual Machine Platform.
Сервер тимчасово працює через Waitress.

