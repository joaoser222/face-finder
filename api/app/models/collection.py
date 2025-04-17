from tortoise import fields, models
from .base import BaseModel

class CollectionStatus:
    UNPACKING = 0
    INDEXING = 1
    FINISHED = 2

class Collection(BaseModel):
    name = fields.CharField(max_length=100, unique=True)
    user = fields.ForeignKeyField('models.User', related_name='collections')
    thumbnail_photo = fields.ForeignKeyField('models.Photo', related_name='collections', null=True, on_delete=fields.SET_NULL)
    status = fields.IntField(default=CollectionStatus.UNPACKING)
    photo_quantity = fields.IntField(default=0)

    class Meta:
        table = "collections"
    
    async def update_photo_data(self):
        from .photo import Photo 
        from app.utils import logger_error
        try:
            photo_quantity = await Photo.filter(owner_type='collection', owner_id=self.id).count()
            self.photo_quantity = photo_quantity

            if(photo_quantity==0):
                self.delete()
                return
            
            photo = await Photo.filter(owner_type='collection', owner_id=self.id).get_or_none()
            
            if photo is not None:
                self.thumbnail_photo_id = photo.id
            
            await self.save()
        except Exception as e:
            logger_error(__name__,e)
            raise

    def __str__(self):
        return self.name
