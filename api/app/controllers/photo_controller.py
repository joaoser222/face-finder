from app.models.photo import Photo
from app.controllers.base_controller import BaseController

class PhotoController(BaseController):
    model = Photo
    prefix = "photos"