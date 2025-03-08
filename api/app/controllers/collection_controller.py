from app.models.collection import Collection
from app.controllers.base_controller import BaseController

class CollectionController(BaseController):
    model = Collection
    prefix = "collections"