from tortoise import fields, models
from typing import Any
from app.utils import generate_unique_filename
import os
import mimetypes
from .base import FileModel

class Photo(FileModel):
    user = fields.ForeignKeyField('models.User', related_name='photos')
    face_count = fields.IntField(default=0)
    is_indexed = fields.BooleanField(default=False) 

    class Meta:
        table = "photos"
    
    async def delete(self, *args, **kwargs):
        # Remove o arquivo salvo localmente
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        # Chama o delete original
        await super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.file_path}"
        
