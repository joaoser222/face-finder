from tortoise import fields, models
from .base import BaseModel

class Search(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='searches')
    name = fields.CharField(max_length=500)
    tolerance_level = fields.IntField()
    photo = fields.ForeignKeyField('models.Photo', related_name='searches')
    collections = fields.JSONField(default=[])

    class Meta:
        table = "searches"

    def __str__(self):
        return self.name
