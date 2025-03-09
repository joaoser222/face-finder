from tortoise import fields, models
from app.models.user import User

class SearchCollection(models.Model):
    id = fields.IntField(pk=True)
    search = fields.ForeignKeyField('models.Search', related_name='search_collections')
    collection = fields.ForeignKeyField('models.Collection', related_name='search_collections')
    photo = fields.ForeignKeyField('models.Photo', related_name='search_collections')
    user = fields.ForeignKeyField('models.User', related_name='search_collections')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "search_collections"

    def __str__(self):
        return f"{self.search_id} - {self.collection_id}"
