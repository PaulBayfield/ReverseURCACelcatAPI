import os 
import importlib


class BlueprintLoader:
    """
    Charge les blueprints des différentes versions de l'API
    """
    def __init__(self, app):
        """
        Constructeur
        """
        self.app = app

        self.loaded = False


    def register(self) -> None:
        """
        Enregistre les routes des différentes versions de l'API
        """
        print("Enregistrement des routes...")

        for version in os.listdir("src/routes"):
            if version.startswith("v"):
                print(f"Charge les routes pour la version {version}")

                blueprint = importlib.import_module(f"src.routes.{version}")

                if not hasattr(blueprint, "__routes__") or len(blueprint.__routes__) == 0:
                    print(f"Blueprint {version} ({blueprint.__version__}) ne contient pas de routes définies! Ignoré...")
                    continue

                print(f"Blueprint {version} ({blueprint.__version__}) possède {len(blueprint.__routes__)} routes: {', '.join([route.name for route in blueprint.__routes__])}")

                for route in blueprint.__routes__:
                    if route.url_prefix:
                        suffix = f"(/{version}{route.url_prefix})"
                    else:
                        suffix = ""

                    print(f"Chargement de la route: {route.name} {suffix}")

                    self.app.blueprint(route)
