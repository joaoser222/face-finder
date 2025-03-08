from app.models.search import Search
from app.controllers.base_controller import BaseController

class SearchController(BaseController):
    model = Search
    prefix = "searches"
