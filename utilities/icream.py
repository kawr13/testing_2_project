import logging
from loguru import logger
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install
import sys
import json
from typing import Any, Optional
from datetime import datetime
import os
from contextlib import contextmanager
import time
from dotenv import load_dotenv
from icecream import ic

# Загрузка переменных окружения
load_dotenv()

# Установка rich для улучшенных трейсбэков
install(show_locals=True)
ic.configureOutput(includeContext=True, contextAbsPath=True, argToStringFunction=repr, prefix='=== ic||')

# Настройка rich-формата
FORMAT = "%(message)s"
console = Console(markup=True)

# Подключение стандартного логгера Python к loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Перехват сообщений от стандартного логгера
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

# Перехватываем стандартные логи
logging.basicConfig(handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)], level="NOTSET")
logging.getLogger().addHandler(InterceptHandler())

# Настройка loguru
log_file = os.getenv("LOG_FILE", "dynamic_logs/app.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logger.add(
    log_file,
    rotation="5 MB",          # Максимальный размер файла
    retention="2 days",       # Сколько хранить логи
    compression="tar",        # Формат сжатия
    serialize=True,           # Записывать в JSON
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
    level="INFO"
)

# Красивое форматирование данных
def pretty_format(data: Any) -> str:
    try:
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=4, ensure_ascii=False, default=str)
        elif isinstance(data, Exception):
            return f"{type(data).__name__}: {str(data)}"
        elif hasattr(data, "__dict__"):
            return json.dumps(
                {k: str(v) if isinstance(v, datetime) else v for k, v in data.__dict__.items()},
                indent=4,
                ensure_ascii=False,
                default=str
            )
        return str(data)
    except Exception as e:
        return f"Error formatting data: {str(e)}"

# Кастомный логгер
class CustomLogger:
    def __init__(self, name: str):
        self.logger = logger.bind(name=name)

    def log(self, level: str, message: str, data: Optional[Any] = None):
        formatted_message = message
        if data:
            formatted_message += "\n" + pretty_format(data)
        self.logger.log(level, formatted_message)

    def info(self, message: str, data: Optional[Any] = None):
        self.log("INFO", message, data)

    def debug(self, message: str, data: Optional[Any] = None):
        self.log("DEBUG", message, data)

    def warning(self, message: str, data: Optional[Any] = None):
        self.log("WARNING", message, data)

    def error(self, message: str, data: Optional[Any] = None):
        self.log("ERROR", message, data)

    def critical(self, message: str, data: Optional[Any] = None):
        self.log("CRITICAL", message, data)

    @contextmanager
    def catch_errors(self, error_message: str = "An error occurred"):
        try:
            yield
        except Exception as e:
            self.error(error_message, e)
            raise

    @contextmanager
    def timer(self, operation_name: str):
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            self.debug(f"{operation_name} took {elapsed_time:.2f} seconds")

# Экземпляр кастомного логгера
log = CustomLogger(name="dynamic_app")

# Пример использования
if __name__ == "__main__":
    log.info("Это информационное сообщение")
    log.debug("Отладка", {"key": "value", "date": datetime.now()})

    # Логирование ошибок
    with log.catch_errors("Ошибка при делении"):
        result = 1 / 0

    # Таймер для операций
    with log.timer("Sleep operation"):
        time.sleep(1)

    class User:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age
            self.created_at = datetime.now()

    user = User("John", 30)
    log.info("Новый пользователь", user)

    # Пример логов от стандартного логгера
    logging.warning("Это системное предупреждение.")
    logging.error("Это системная ошибка.")
