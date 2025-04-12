from tortoise import fields, models
from .base import BaseModel

class Face(BaseModel):
    bbox = fields.JSONField()
    user = fields.ForeignKeyField('models.User', related_name='faces')
    photo = fields.ForeignKeyField('models.Photo', related_name='faces')
    collection = fields.ForeignKeyField('models.Collection', related_name='faces')

    class Meta:
        table = "faces"

    def __str__(self):
        return self.id

