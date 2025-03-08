from app.models.user import User
from app.controllers.base_controller import BaseController

class UserController(BaseController):
    model = User
    prefix = "users"

