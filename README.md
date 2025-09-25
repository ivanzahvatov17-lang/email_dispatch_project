# Email Dispatch Project 
## Кратко
Прототип системы автоматических email-рассылок (демо) на Python:
- Backend: FastAPI (REST API)
- Frontend: PyQt6 (настольный клиент)
- DB: дамп PostgreSQL (`db_dump.sql`) — для локального теста приложение по умолчанию использует SQLite.

## Запуск (локально для разработки)
1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt

