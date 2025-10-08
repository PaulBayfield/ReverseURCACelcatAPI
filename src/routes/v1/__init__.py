from .agenda.v1_agenda import bp as RouteAgenda
from .service.v1_service import bp as RouteService


# Meta données de la version
__version__ = "1.0.0"
__author__ = "Paul Bayfield"
__description__ = "/v1 pour l'API ReverseURCACelcat"
__routes__ = [
    RouteAgenda,
    RouteService
]


__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "__routes__"
]
