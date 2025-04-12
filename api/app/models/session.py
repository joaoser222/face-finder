from tortoise import fields, models
from .base import BaseModel

class Session(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="sessions")
    token = fields.CharField(max_length=255, unique=True)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "sessions"