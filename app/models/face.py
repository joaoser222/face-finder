from tortoise import fields, models

class Face(models.Model):
    id = fields.IntField(pk=True)
    bbox = fields.JSONField()
    user_id = fields.ForeignKeyField('models.User', related_name='faces')
    photo_id = fields.ForeignKeyField('models.Photo', related_name='faces')
    collection_id = fields.ForeignKeyField('models.Collection', related_name='faces')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)


    class Meta:
        table = "faces"

    def __str__(self):
        return self.id

