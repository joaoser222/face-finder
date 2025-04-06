from tortoise import fields, models

class Queue(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='queues')
    status = fields.IntField(default=0)
    process_type = fields.CharField(max_length=50)
    owner_type = fields.CharField(max_length=20)
    owner_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "queues"

    def __str__(self):
        return str(self.id)
