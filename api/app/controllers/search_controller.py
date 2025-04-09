from app.models.search import Search
from .view_controller import ViewController

class SearchController(ViewController):
    model = Search
    prefix = "searches"
