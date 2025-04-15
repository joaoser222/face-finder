from tortoise import fields, models
from .base import PolymorphicModel

class JobStatus:
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = -1

class Job(PolymorphicModel):
    status = fields.IntField(default=JobStatus.PENDING)
    process_type = fields.CharField(max_length=50)

    class Meta:
        table = "jobs"

    def __str__(self):
        return str(self.id)
