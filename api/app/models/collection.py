from tortoise import fields, models
from app.models.file import File

class Collection(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    user = fields.ForeignKeyField('models.User', related_name='collections')
    thumbnail_file = fields.ForeignKeyField('models.File', related_name='collections', null=True)
    status = fields.IntField(default=0)
    photo_quantity = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "collections"

    def __str__(self):
        return self.name
