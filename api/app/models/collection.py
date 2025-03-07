from tortoise import fields, models

class Collection(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    user_id = fields.ForeignKeyField('models.User', related_name='collections')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "collections"

    def __str__(self):
        return self.name
