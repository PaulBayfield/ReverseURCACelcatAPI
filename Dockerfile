FROM sanicframework/sanic:lts-py3.11
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --no-cache git

COPY . ./ReverseURCACelcatAPI

WORKDIR /ReverseURCACelcatAPI

RUN uv sync --frozen

EXPOSE 7000

CMD ["uv", "run", "__main__.py"]
