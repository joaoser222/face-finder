from tortoise import fields, models
from typing import Any
import os
import mimetypes

class BaseModel(models.Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        abstract = True 

class PolymorphicModel(BaseModel):
    owner_type = fields.CharField(max_length=20)  # 'collection', 'search', etc.
    owner_id = fields.IntField()

    class Meta:
        abstract = True
    
    @classmethod
    def set_owner(cls, owner: Any):
        cls.owner_type = owner.__class__.__name__.lower()
        cls.owner_id = owner.id

class FileModel(PolymorphicModel):
    original_name = fields.CharField(max_length=500)
    file_path = fields.CharField(max_length=500)
    extension_type = fields.CharField(max_length=100)
    mime_type = fields.CharField(max_length=100)
    size = fields.IntField()  # Tamanho em bytes
    user = fields.ForeignKeyField('models.User', related_name='files')

    class Meta:
        abstract = True  # Isso torna o modelo abstrato

    # Factory method para criar arquivos
    @classmethod
    async def create_file(
        cls,
        owner: Any,  # Models relacionadas,
        file_name: str,
        file_size: int
    ) -> 'FileModel':
        """Cria um novo arquivo associado a uma entidade dona."""
        try:
            from app.utils import generate_unique_filename
            owner_type = owner.__class__.__name__.lower()
            unique_filename = generate_unique_filename(file_name)
            mime_type, _ = mimetypes.guess_type(unique_filename)
            basename,ext = os.path.splitext(unique_filename)
            file = await cls.create(
                user_id=owner.user_id,
                original_name=file_name,
                file_path=f"/app/files/{owner_type}/{owner.id}/{unique_filename}",
                extension_type=ext,
                mime_type=mime_type,
                size=file_size,
                owner_type=owner_type,
                owner_id=owner.id,
            )
            return file
        except Exception as e:
            raise

    