from tortoise.models import Model
from tortoise import fields

class Session(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="sessions")
    token = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "sessions"