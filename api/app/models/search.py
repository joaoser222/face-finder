from tortoise import fields, models
from .base import BaseModel

class SearchStatus:
    WAITING = 0
    PROCESSING = 1
    FINISHED = 2
class Search(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='searches')
    name = fields.CharField(max_length=500)
    tolerance_level = fields.IntField()
    status = fields.IntField(default=SearchStatus.WAITING)
    collections = fields.JSONField(default=[])

    class Meta:
        table = "searches"

    def __str__(self):
        return self.name
