from app.models.search import Search
from app.controllers.base_controller import BaseController

class SearchController(BaseController):
    def __init__(self):
        super().__init__()
        self.model = Search
        self.endpoint = "searches"
