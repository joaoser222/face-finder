from tortoise import fields, models
from .base import BaseModel

class User(BaseModel):
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    tolerance_level = fields.IntField(default=70)

    class Meta:
        table = "users"
    
    def visible_fields(self):
        return {
            "username": self.username,
            "email": self.email,
            "tolerance_level": self.tolerance_level,
        }

    def __str__(self):
        return self.username
