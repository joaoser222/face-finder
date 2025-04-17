from tortoise import fields, models
from .base import BaseModel

class CollectionStatus:
    UNPACKING = 0
    INDEXING = 1
    FINISHED = 2

class Collection(BaseModel):
    name = fields.CharField(max_length=100, unique=True)
    user = fields.ForeignKeyField('models.User', related_name='collections')
    thumbnail_photo = fields.ForeignKeyField('models.Photo', related_name='collections', null=True, on_delete=fields.SET_NULL)
    status = fields.IntField(default=CollectionStatus.UNPACKING)
    photo_quantity = fields.IntField(default=0)

    class Meta:
        table = "collections"

    def __str__(self):
        return self.name
