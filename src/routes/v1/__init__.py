from .agenda.v1_agenda import bp as RouteAgenda


# Meta données de la version
__version__ = "1.0.0"
__author__ = "Paul Bayfield"
__description__ = "/v1 pour l'API ReverseURCACelcat"
__routes__ = [
    RouteAgenda,
]


__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "__routes__"
]
