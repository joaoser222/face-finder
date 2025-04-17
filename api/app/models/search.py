from tortoise import fields, models
from .base import BaseModel

class SearchStatus:
    WAITING = 0
    PROCESSING = 1
    FINISHED = 2

class Search(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='searches')
    name = fields.CharField(max_length=500)
    thumbnail_photo = fields.ForeignKeyField('models.Photo', related_name='searches', null=True,on_delete=fields.SET_NULL)
    tolerance_level = fields.IntField(default=60)
    status = fields.IntField(default=SearchStatus.WAITING)
    collections = fields.JSONField(default=[])

    class Meta:
        table = "searches"

    def __str__(self):
        return self.name
