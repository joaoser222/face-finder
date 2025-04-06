from tortoise import fields, models
from typing import Any
from app.utils import generate_unique_filename
import os

class File(models.Model):
    id = fields.IntField(pk=True)
    original_name = fields.CharField(max_length=500)
    file_path = fields.CharField(max_length=500)
    extension_type = fields.CharField(max_length=100)
    size = fields.IntField()  # Tamanho em bytes
    
    # Relações polimórficas (pode ser Collection, Search, etc.)
    owner_type = fields.CharField(max_length=20)  # 'collection', 'search', etc.
    owner_id = fields.IntField()
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "files"
        unique_together = (("owner_type", "owner_id", "file_path"),)

    def __str__(self):
        return f"{self.owner_type}_{self.owner_id}/{self.file_path}"

    # Factory method para criar arquivos
    @classmethod
    async def create_file(
        cls,
        owner: Any,  # Models relacionadas
        file_name: str,
        file_size: int
    ) -> 'File':
        """Cria um novo arquivo associado a uma entidade dona."""
        try:
            owner_type = owner.__class__.__name__.lower()
            unique_filename = generate_unique_filename(file_name)
            _,ext = os.path.splitext(unique_filename)
            file = await cls.create(
                original_name=file_name,
                file_path=f"/app/files/{owner_type}/{owner.id}/{unique_filename}",
                extension_type=ext,
                size=file_size,
                owner_type=owner_type,
                owner_id=owner.id,
            )
            return file
        except Exception as e:
            raise
        
