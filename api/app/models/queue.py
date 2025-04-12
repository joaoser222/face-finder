from tortoise import fields, models
from .base import PolymorphicModel

class Queue(PolymorphicModel):
    user = fields.ForeignKeyField('models.User', related_name='queues')
    status = fields.IntField(default=0)
    process_type = fields.CharField(max_length=50)

    class Meta:
        table = "queues"

    def __str__(self):
        return str(self.id)
