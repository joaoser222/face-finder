from tortoise import fields, models
class Photo(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.ForeignKeyField('models.User', related_name='photos')
    collection_id = fields.ForeignKeyField('models.Collection', related_name='photos')
    original_name = fields.CharField(max_length=500)
    file_path = fields.CharField(max_length=500)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)


    class Meta:
        table = "photos"

    def __str__(self):
        return self.file_path
