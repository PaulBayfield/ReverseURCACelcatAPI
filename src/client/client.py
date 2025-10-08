from .cas import CAS
from .config import config
from .exceptions import InvalidCredentials
from urllib.parse import urlencode, urljoin
from aiohttp import ClientSession


class Client(CAS):
    """
    Client pour interagir avec le service Celcat de l'URCA
    """
    def __init__(self, session: ClientSession) -> None:
        """
        Initialise le client avec une session HTTP

        :param session: Session HTTP aiohttp
        :type session: ClientSession
        """
        super().__init__(session)

        self.CAS_BASE_URL = config.get('cas').get('BASE_URL')
        self.SERVICE_URL = config.get('service').get('BASE_URL')

    async def login(self, username: str, password: str) -> bool:
        """
        Connection au Service
        
        :param username: Nom d'utilisateur
        :type username: str
        :param password: Mot de passe
        :type password: str
        :return: Un booleen indiquant si la connection a reussi
        :rtype: bool
        """
        url = f"{self.CAS_BASE_URL}?service={self.SERVICE_URL}"

        data = {
            "username": username,
            "password": password,
            "execution": await self.getTokenData(url),
            "_eventId": "submit",
            "geolocation": ""
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": config.get('userAgent')
        }

        resp = await self.request(
            url=url,
            method="POST",
            data=urlencode(data),
            headers=headers,
            raw=True, 
            redirect=False
        )

        location = resp.headers.get("location", "")

        if "ticket" in location:
            return await self.createSession(location)
        else:
            raise InvalidCredentials("Impossible de se connecter avec les identifiants fournis ! Vérifiez-les et réessayez.")


    async def agenda(self, group_id: str) -> str:
        """
        Récupère l'agenda du groupe demandé

        :param group_id: ID du groupe (ex: g30029)
        :type group_id: str
        :return: L'agenda au format XML
        :rtype: str
        """
        url = urljoin(self.SERVICE_URL, f"{group_id}.xml")

        res = await self.request(
            url=url,
            method="GET"
        )
        
        return res
