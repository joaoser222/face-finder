from app.models.photo import Photo
from app.controllers.base_controller import BaseController

class PhotoController(BaseController):
    def __init__(self):
        super().__init__()
        self.model = Photo
        self.endpoint = "photos"
