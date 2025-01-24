from tortoise import Tortoise
from utilities.icream import ic, log


TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["models.model", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init():
    log.info("Init DB")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close():
    log.info("Close DB")
    await Tortoise.close_connections()