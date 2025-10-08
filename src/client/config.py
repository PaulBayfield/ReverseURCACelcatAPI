from . import __version__


config = {
    "userAgent": f"Reverse URCA Celcat {__version__}",

    "service": {
        "BASE_URL": "https://celcat-auth.univ-reims.fr/910913/"
    },

    "cas": {
        "BASE_URL": "https://cas.univ-reims.fr/cas/login"
    },

}
