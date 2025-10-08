from .config import config
from .exceptions import UnknownError, UnknownAgenda
from bs4 import BeautifulSoup
from aiohttp import ClientSession


class CAS:
    """
    Classe de base pour gérer l'authentification CAS
    """
    def __init__(self, session: ClientSession) -> None:
        """
        Initialise la classe CAS avec une session HTTP

        :param session: Session HTTP aiohttp
        :type session: ClientSession
        """
        self.session = session

        self.BASE_URL = config.get('service').get('BASE_URL')

        self.headers = {
            "User-Agent": config.get('userAgent'),
        }


    async def request(self, url: str, method: str, data: dict = None, headers: dict = None, redirect: bool = True, raw: bool = False) -> str:
        """
        Permet d'effectuer une requête HTTP avec la session courante

        :param url: URL de la requête
        :type url: str
        :param method: Méthode HTTP (GET, POST, etc.)
        :type method: str
        :param data: Données à envoyer avec la requête (pour les méthodes POST, PUT, etc.)
        :type data: dict, optional
        :param headers: En-têtes HTTP personnalisés
        :type headers: dict, optional
        :param redirect: Indique si les redirections doivent être suivies
        :type redirect: bool, optional
        :param raw: Indique si la réponse brute doit être retournée (True) ou le texte (False)
        :type raw: bool, optional
        :return: La réponse de la requête (texte, JSON, ou objet ClientResponse brut selon les paramètres)
        :rtype: str
        """
        if headers:
            hd = headers
        else:
            hd = self.headers

        async with self.session.request(method, url, data=data, headers=hd, allow_redirects=redirect) as response:
            if raw:
                return response
            else:
                if response.status in [200, 201]:
                    return await response.text()
                else:
                    if response.status == 404:
                        raise UnknownAgenda()
                    else:
                        raise UnknownError(f"Erreur lors de la requête HTTP ! Statut: {response.status}")

    async def createSession(self, redirectURL: str) -> bool:
        """
        Permet de récupérer le cookie PHPSESSID
        
        :param redirectURL: URL de redirection
        :type redirectURL: str
        :return: Un booleen indiquant si la connection a reussi
        :rtype: bool
        """
        resp = await self.request(
            url=redirectURL,
            method="GET",
            redirect=False,
            raw=True
        )

        cookies = resp.headers.get("set-cookie", [])
        PHPSESSID = cookies

        if PHPSESSID:
            return True
        else:
            raise UnknownError("Impossible de récupérer le cookie PHPSESSID !")


    async def getTokenData(self, url: str) -> str:
        """
        Permet de récupérer le token d'authentification
        
        :param url: URL de la requête
        :type url: str
        :return: Token d'authentification
        :rtype: str
        """
        resp = await self.request(
            url=url,
            method="GET"
        )

        b = BeautifulSoup(resp, "html.parser")
        data = b.find_all("input", {"type": "hidden"})
        if len(data) > 0:
            return str(data[0]).split("value=\"")[1].split("\"/>")[0]
        else:
            UnknownError("Impossible de récupérer le token d'authentification !")
