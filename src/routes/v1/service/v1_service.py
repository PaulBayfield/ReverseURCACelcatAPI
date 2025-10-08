from ....components.ratelimit import ratelimit
from ....components.response import JSON
from ....models.responses import Status
from ....models.exceptions import RateLimited
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Service",
    url_prefix="/",
    version=1,
    version_prefix="v"
)


# /status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="Statut de l'API",
    description="Retourne le statut de l'API.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={
        "application/json": Status
    },
    description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
async def getStatus(request: Request) -> JSONResponse:
    """
    Retourne le statut de l'API.

    :return: JSONResponse
    """
    return JSON(
        request=request,
        success=True,
        message="L'API est en ligne.",
        status=200,
    ).generate()
