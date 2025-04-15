from tortoise import fields, models
from .base import BaseModel
import os
from pathlib import Path

class Face(BaseModel):
    data = fields.JSONField()
    user = fields.ForeignKeyField('models.User', related_name='faces')
    photo = fields.ForeignKeyField('models.Photo', related_name='faces')

    class Meta:
        table = "faces"

    def __str__(self):
        return self.id
    
    async def get_face_path(self) -> str:
        """
        Retorna o caminho da face

        Returns:
            str: O caminho da face
        """
        photo = await self.photo
        original_path = Path(photo.file_path)
        face_dir = original_path.parent / "faces"
        
        return str(f"{face_dir}/{self.id}{photo.extension_type}")
