import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    """Логирование для бота"""
    os.makedirs("logs", exist_ok=True)

    # Настройка логирования в файл
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Создание обработчика для записи логов в файл
    file_handler = RotatingFileHandler(
        "logs/log.txt", maxBytes=10485760, backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # обработчик для записи логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавление обработчиков в логгер
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # добавление уровня логирования для модулей
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
