from tortoise import fields, models
from typing import Any
from app.utils import generate_unique_filename
import os
import mimetypes
from .base import FileModel

class Archive(FileModel):
    original_name = fields.CharField(max_length=500)
    file_path = fields.CharField(max_length=500)
    extension_type = fields.CharField(max_length=100)
    mime_type = fields.CharField(max_length=100)
    size = fields.IntField()  # Tamanho em bytes
    user = fields.ForeignKeyField('models.User', related_name='archives')

    class Meta:
        table = "archives"

    def __str__(self):
        return f"{self.file_path}"
        
