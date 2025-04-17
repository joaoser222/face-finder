from tortoise import fields, models
from .base import BaseModel
import os,shutil
class SearchStatus:
    WAITING = 0
    PROCESSING = 1
    FINISHED = 2

class Search(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='searches')
    name = fields.CharField(max_length=500)
    thumbnail_photo = fields.ForeignKeyField('models.Photo', related_name='searches', null=True,on_delete=fields.SET_NULL)
    tolerance_level = fields.IntField(default=60)
    status = fields.IntField(default=SearchStatus.WAITING)
    collections = fields.JSONField(default=[])

    class Meta:
        table = "searches"
    
    async def delete(self, *args, **kwargs):
        # Lógica pré-delete
        search_path = f"/app/files/search/{self.id}"
        if os.path.exists(search_path):
            shutil.rmtree(search_path)

        # Chama o delete original
        await super().delete(*args, **kwargs)

       
    def __str__(self):
        return self.name
