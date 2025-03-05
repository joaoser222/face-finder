from app.models.user import User
from app.controllers.base_controller import BaseController

class UserController(BaseController):

    def __init__(self):
        super().__init__()
        self.model = User
        self.endpoint = "users"

