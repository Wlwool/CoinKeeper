Базовые команды:

/start — приветствие, инструкция.   
/help — список команд.  
/cancel — отмена текущей операции.

---

Управление транзакциями:
/add_income [сумма] [категория] — добавить доход.
/add_expense [сумма] [категория] — добавить расход.
/delete_transaction [id] — удалить запись.
/history [N дней] — история операций.

---

Статистика и отчеты:
/stats [месяц] — расходы по категориям.
/export_csv — выгрузка данных в CSV.
/plot — график расходов за период.

---

Категории и настройки:
/set_limit [категория] [лимит] — установить лимит.
/add_category [название] — создать категорию.

---

Дополнительные функции:
Автоматическая категоризация по ключевым словам (например, "магнит" → "продукты").
Уведомления о приближении к лимиту.
Конвертация валют через API (например, exchangerate-api.com).

---

Библиотеки:
Для бота: aiogram
Для БД: SQLAlchemy + asyncpg (для асинхронного доступа).
Валидация: pydantic
Даты: pendulum.
Отчеты: pandas, openpyxl.
Графики: matplotlib.

