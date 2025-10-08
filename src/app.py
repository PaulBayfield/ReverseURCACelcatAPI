from sanic import Sanic
from .config import AppConfig
from .client import Client
from .components.middleware import Middleware
from .components.ratelimit import Ratelimiter
from .components.cache import Cache
from .components.blueprint import BlueprintLoader
from .components.statistics import PrometheusStatistics
from .components.errors import ErrorHandler
from dotenv import load_dotenv
from os import environ
from textwrap import dedent
from aiohttp import ClientSession
from datetime import datetime
from pytz import timezone


load_dotenv(dotenv_path=".env")


# Initialisation de l'application
app = Sanic(
    name="ReverseURCACelcatAPI",
    config=AppConfig(),
)

# Ajoute des informations à la documentation OpenAPI
app.ext.openapi.raw(
    {
        "servers": [
            {
                "url": f"{environ.get('API_DOMAIN')}",
                "description": "Serveur de production"
            }
        ],
    }
)

year = datetime.now(
    tz=timezone("Europe/Paris")
).year

app.ext.openapi.describe(
    title=app.name,
    version=f"v{app.config.API_VERSION}",
    description=dedent(
        f"""
            # 📝 • Introduction
            ReverseURCACelcatAPI est une API REST non officielle pour accéder aux données de CELCAT afin de récupérer les informations des emplois du temps, sans authentification, pour pouvoir ajouter les emplois du temps dans des applications tierces tel que Google Agenda, Outlook, etc...
               
            ⁣  
            💻 *Si vous souhaitez contribuer au projet, vous pouvez consulter le dépôt sur GitHub : [github.com/PaulBayfield/ReverseURCACelcatAPI](https://github.com/PaulBayfield/ReverseURCACelcatAPI) !*  
            ⁣
            # ⚙️ • Données
            - Les données sont mises en cache pendant 1 heure pour minimiser la charge sur le serveur d'authentification CAS de l'URCA et le serveur CELCAT.
            - Toutes les dates sont stockées en UTC+1 (Europe/Paris).
            - Les données sont fournies "telles quelles" sans aucune garantie.
               
            ⁣  
            # 📄 • Termes d'utilisation
            Il y a quelques règles à respecter pour toute utilisation de l'API :
            - Vous ne pouvez pas utiliser l'API pour des activités illégales / malveillantes.
            - Vous ne devez pas abuser de l'API (limite de 100 requêtes par minute), l'utilisation de plusieurs adresses IP pour contourner cette limite est interdite.  
               
            ⁣  
            ⚠️ ***Tout abus de l'API entraînera un bannissement temporaire ou définitif.***
               
            ⁣  
            # 📩 • Contact
            Pour toute question, suggestion, bug, ou problème n'hésitez pas à me contacter !  
            - E-mail : [paul@bayfield.dev](mailto:paul@bayfield.dev)  
            - GitHub : [github.com/PaulBayfield/ReverseURCACelcatAPI](https://github.com/PaulBayfield/ReverseURCACelcatAPI)  
              
            ⁣  
            **Paul Bayfield @ 2025 - {year} | Tous droits réservés.**  
            *Ce site n'est pas affilié à l'URCA (Université de Reims Champagne-Ardenne) ou à CELCAT.*  
        """
    ),
)

# Ajoute les statistiques Prometheus
PrometheusStatistics(app)

# Enregistrement du rate limiter
app.ctx.ratelimiter = Ratelimiter()

# Enregistrement des middlewares
Middleware(app)

# Enregistrement du cache
app.ctx.cache = Cache(app)

# Enregistrement des routes
BlueprintLoader(app).register()

# Enregistrement des erreurs
ErrorHandler(app)


@app.listener("before_server_start")
async def setup_app(app: Sanic, loop):
    app.ctx.session = ClientSession()
    
    app.ctx.client = Client(
        session=app.ctx.session,
    )
    await app.ctx.client.login(
        username=environ.get("URCA_USERNAME"),
        password=environ.get("URCA_PASSWORD"),
    )
    app.ctx.client_created = datetime.now(
        tz=timezone("Europe/Paris")
    )

    print("API démarrée")


@app.listener("after_server_stop")
async def close_app(app: Sanic, loop):
    await app.ctx.session.close()

    print("API arrêtée")
