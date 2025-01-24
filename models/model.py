from icecream import ic
from tortoise import fields
from tortoise.models import Model
from datetime import datetime, timedelta, time


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.IntField(unique=True)
    jwt_token = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)


class Imei(Model):
    id = fields.IntField(pk=True)
    imei = fields.CharField(max_length=15, unique=True)
    json_data = fields.JSONField()