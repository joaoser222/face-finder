from tortoise import fields, models
from app.models.user import User

class SearchFace(models.Model):
    id = fields.IntField(pk=True)
    search = fields.ForeignKeyField('models.Search', related_name='search_faces')
    face = fields.ForeignKeyField('models.Face', related_name='search_faces')
    user = fields.ForeignKeyField('models.User', related_name='search_faces')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "search_faces"

    def __str__(self):
        return f"{self.search_id} - {self.face_id}"
