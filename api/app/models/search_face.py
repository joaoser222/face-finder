from tortoise import fields, models
from .base import BaseModel

class SearchFace(BaseModel):
    similarity = fields.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    search = fields.ForeignKeyField('models.Search', related_name='search_faces')
    face = fields.ForeignKeyField('models.Face', related_name='search_faces')
    photo = fields.ForeignKeyField('models.Photo', related_name='search_faces')
    user = fields.ForeignKeyField('models.User', related_name='search_faces')

    class Meta:
        table = "search_faces"

    def __str__(self):
        return f"{self.search_id} - {self.face_id}"
