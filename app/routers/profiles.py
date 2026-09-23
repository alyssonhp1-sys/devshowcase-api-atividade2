from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProfileCreate, ProfileResponse
from app.services import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def criar_perfil(dados: ProfileCreate, db: Session = Depends(get_db)):
    return ProfileService(db).criar(dados)


@router.get("/{id}", response_model=ProfileResponse)
def buscar_perfil(id: int, db: Session = Depends(get_db)):
    return ProfileService(db).buscar(id)
