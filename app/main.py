import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Route

from app.database import create_tables
from app.exceptions import AppError
from app.routers import profiles, projects, technologies

create_tables()

logger = logging.getLogger("devshowcase")

_FRASES_HTTP = {
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    500: "Internal Server Error",
}

app = FastAPI(
    title="DevShowcase API",
    description=(
        "API acadêmica para cadastrar perfis, tecnologias e projetos de desenvolvedores, "
        "com feedback, média, upvote e listagem paginada."
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(profiles.router)
app.include_router(technologies.router)
app.include_router(projects.router)

# O HTML padrão do FastAPI 0.141 referencia SwaggerUIStandalonePreset,
# que não existe mais no swagger-ui-dist@5 e deixa /docs em branco.
app.router.routes = [
    rota
    for rota in app.router.routes
    if not (isinstance(rota, Route) and rota.path == "/docs")
]


@app.get("/docs", include_in_schema=False)
def swagger_docs():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>DevShowcase API - Swagger UI</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"/>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
        deepLinking: true
      });
    </script>
  </body>
</html>
"""
    )


def _corpo_erro(status_code: int, message: str, error: str | None = None) -> dict:
    return {
        "status": status_code,
        "error": error or _FRASES_HTTP.get(status_code, "Error"),
        "message": message,
    }


def _mensagem_validacao(exc: RequestValidationError) -> str:
    partes: list[str] = []
    for erro in exc.errors():
        local = [
            str(item)
            for item in erro.get("loc", [])
            if item not in {"body", "query", "path"}
        ]
        campo = ".".join(local) if local else "requisição"
        partes.append(f"Campo '{campo}' inválido.")
    if not partes:
        return "Requisição inválida."
    return " ".join(dict.fromkeys(partes))


@app.exception_handler(AppError)
async def tratar_erro_aplicacao(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=_corpo_erro(exc.status_code, exc.message, exc.error),
    )


@app.exception_handler(StarletteHTTPException)
async def tratar_http_exception(request: Request, exc: StarletteHTTPException):
    mensagem = (
        exc.detail
        if isinstance(exc.detail, str)
        else "Não foi possível processar a requisição."
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_corpo_erro(exc.status_code, mensagem),
    )


@app.exception_handler(RequestValidationError)
async def tratar_validacao(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_corpo_erro(422, _mensagem_validacao(exc)),
    )


@app.exception_handler(Exception)
async def tratar_erro_interno(request: Request, exc: Exception):
    logger.exception("Erro interno inesperado")
    return JSONResponse(
        status_code=500,
        content=_corpo_erro(
            500,
            "Ocorreu um erro interno. Tente novamente mais tarde.",
        ),
    )
