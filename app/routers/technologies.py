from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TechnologyCreate, TechnologyResponse
from app.services import TechnologyService

router = APIRouter(prefix="/api/technologies", tags=["Technologies"])


@router.post("", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
def criar_tecnologia(dados: TechnologyCreate, db: Session = Depends(get_db)):
    return TechnologyService(db).criar(dados)


@router.get("", response_model=list[TechnologyResponse])
def listar_tecnologias(db: Session = Depends(get_db)):
    return TechnologyService(db).listar()
