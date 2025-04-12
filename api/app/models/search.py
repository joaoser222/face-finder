from tortoise import fields, models
from .base import BaseModel

class Search(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='searches')
    original_name = fields.CharField(max_length=500)
    tolerance_level = fields.IntField()
    file = fields.ForeignKeyField('models.File', related_name='searches')
    collections = fields.JSONField(default=[])

    class Meta:
        table = "searches"

    def __str__(self):
        return self.file_path
