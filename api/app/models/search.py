from tortoise import fields, models
from app.models.user import User

class Search(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='searches')
    original_name = fields.CharField(max_length=500)
    tolerance_level = fields.IntField()
    file = fields.ForeignKeyField('models.File', related_name='searches')
    collections = fields.JSONField(default=[])
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)


    class Meta:
        table = "searches"

    def __str__(self):
        return self.file_path
