from app.models.collection import Collection
from app.controllers.base_controller import BaseController

class CollectionController(BaseController):
    def __init__(self):
        super().__init__()
        self.model = Collection
        self.endpoint = "collections"