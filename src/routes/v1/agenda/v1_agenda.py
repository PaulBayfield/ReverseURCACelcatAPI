from ....client import UnknownAgenda, UnknownError
from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.response import JSON, Raw
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....utils.xml_to_ics import convert_xml_to_ics
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Agenda",
    url_prefix="/",
    version=1,
    version_prefix="v"
)


# /agenda/<group>
@bp.route("/agenda/<group>", methods=["GET"])
@openapi.definition(
    summary="Obtenir l'agenda d'un groupe",
    description="Retourne l'agenda d'un groupe au format iCalendar (ICS) pour une intégration facile dans des applications tierces comme Google Agenda, Outlook, etc.\n\nPour obtenir l'ID d'un groupe vous devez vous connecter à l'interface CELCAT de votre établissement, aller dans la section des emplois du temps, sélectionner le groupe souhaité, puis copier l'ID du groupe depuis l'URL.\n\nPour des raisons de sécurité et de confidentialité, l'API ne révèle pas si un groupe existe ou non. Si le groupe n'existe pas, un agenda vide sera retourné.",
    tag="Agenda"
)
@inputs(
    Argument(
        name="group",
        description="ID du groupe",
        methods={
            "group": Rules.group
        },
        call=str,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(
    ttl=60 * 60,  # 1 heure,
)
async def getAgenda(request: Request, group: str) -> JSONResponse:
    """
    Retourne les statistiques de l'API.

    :return: JSONResponse
    """
    try:
        agenda = await request.app.ctx.client.agenda(
            group_id=group,
        )
    except UnknownAgenda:
        # return JSON(
        #     request=request,
        #     success=False,
        #     message="Groupe inconnu !",
        #     status=404
        # ).generate()

        # Pour éviter de révéler l'existence ou non d'un groupe, on retourne un agenda vide
        agenda = "<calendar></calendar>"
    except UnknownError:
        return JSON(
            request=request,
            success=False,
            message="Une erreur inconnue est survenue lors de la récupération de l'agenda !",
            status=500
        ).generate()

    ics = await convert_xml_to_ics(agenda)

    return Raw(
        request=request,
        success=True,
        data=ics,
        status=200,
        content_type="text/calendar",
    ).generate()
