class InvalidCredentials(Exception):
    """
    Exception levée pour des identifiants invalides
    """
    def __init__(self, error: str) -> None:
        """
        Initialise l'exception avec un message d'erreur

        :param error: Message d'erreur
        :type error: str
        """
        self.error = error
        super().__init__(self.error)


class UnknownError(Exception):
    """
    Exception levée pour une erreur inconnue
    """
    def __init__(self, error: str) -> None:
        """
        Initialise l'exception avec un message d'erreur

        :param error: Message d'erreur
        :type error: str
        """
        self.error = error
        super().__init__(self.error)


class UnknownAgenda(Exception):
    """
    Exception levée pour un agenda inconnu
    """
    def __init__(self, error: str = "Agenda inconnu") -> None:
        """
        Initialise l'exception avec un message d'erreur

        :param error: Message d'erreur
        :type error: str
        """
        self.error = error
        super().__init__(self.error)
