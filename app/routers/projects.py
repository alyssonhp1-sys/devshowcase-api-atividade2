from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ErrorResponse,
    FeedbackCreate,
    FeedbackResponse,
    ProjectCreate,
    ProjectPage,
    ProjectResponse,
)
from app.services import FeedbackService, ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projects"])

_respostas_erro = {
    400: {"model": ErrorResponse, "description": "Requisição inválida."},
    404: {"model": ErrorResponse, "description": "Registro não encontrado."},
}


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def criar_projeto(dados: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService(db).criar(dados)


@router.get(
    "",
    response_model=ProjectPage,
    summary="Lista projetos com filtro opcional e paginação",
    responses={400: _respostas_erro[400]},
)
def listar_projetos(
    technology: str | None = Query(
        default=None,
        description="Filtra pelo nome da tecnologia. Opcional.",
    ),
    page: int = Query(default=1, description="Número da página. Começa em 1."),
    size: int = Query(
        default=10,
        description="Quantidade de itens por página, de 1 a 100.",
    ),
    db: Session = Depends(get_db),
):
    return ProjectService(db).listar(technology, page, size)


@router.post(
    "/{id}/feedbacks",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um feedback com nota de 1 a 5",
    responses=_respostas_erro,
)
def criar_feedback(id: int, dados: FeedbackCreate, db: Session = Depends(get_db)):
    return FeedbackService(db).criar(id, dados)


@router.put(
    "/{id}/upvote",
    response_model=ProjectResponse,
    summary="Incrementa o upvote do projeto",
    responses={404: _respostas_erro[404]},
)
def registrar_upvote(id: int, db: Session = Depends(get_db)):
    return ProjectService(db).registrar_upvote(id)
