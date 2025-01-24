from ast import Set
from ctypes.wintypes import HSTR
from dataclasses import dataclass
import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    TOKEN: str|None = os.getenv("BOT_TOKEN")
    WEBHOOK_URL: str|None = os.getenv("WEBHOOK_URL")
    WEBHOOK_PATH: str|None = os.getenv("WEBHOOK_PATH", '/webhook')
    WEBHOOK_HOST: str|None = os.getenv("WEBHOOK_HOST", 'localhost')
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", 8000))


settings = Settings()