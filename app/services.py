import math

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import Feedback, Profile, Project, Technology
from app.repositories import (
    FeedbackRepository,
    ProfileRepository,
    ProjectRepository,
    TechnologyRepository,
)
from app.schemas import FeedbackCreate, ProfileCreate, ProjectCreate, TechnologyCreate

TAMANHO_MAXIMO = 100


def calcular_media(notas: list[int]) -> float:
    if not notas:
        return 0.0
    return round(sum(notas) / len(notas), 2)


class ProfileService:
    def __init__(self, db: Session):
        self.repositorio = ProfileRepository(db)

    def criar(self, dados: ProfileCreate) -> Profile:
        perfil = Profile(
            name=dados.name,
            bio=dados.bio,
            github_url=str(dados.github_url) if dados.github_url else None,
            linkedin_url=str(dados.linkedin_url) if dados.linkedin_url else None,
        )
        return self.repositorio.create(perfil)

    def buscar(self, profile_id: int) -> Profile:
        perfil = self.repositorio.get_by_id(profile_id)
        if perfil is None:
            raise NotFoundError("Perfil não encontrado.")
        return perfil


class TechnologyService:
    def __init__(self, db: Session):
        self.db = db
        self.repositorio = TechnologyRepository(db)

    def criar(self, dados: TechnologyCreate) -> Technology:
        if self.repositorio.get_by_name(dados.name) is not None:
            raise ConflictError("Já existe uma tecnologia com este nome.")
        tecnologia = Technology(name=dados.name)
        try:
            return self.repositorio.create(tecnologia)
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Já existe uma tecnologia com este nome.")

    def listar(self) -> list[Technology]:
        return self.repositorio.get_all()


class ProjectService:
    def __init__(self, db: Session):
        self.projetos = ProjectRepository(db)
        self.perfis = ProfileRepository(db)
        self.tecnologias = TechnologyRepository(db)

    def criar(self, dados: ProjectCreate) -> Project:
        if self.perfis.get_by_id(dados.profile_id) is None:
            raise NotFoundError("Perfil informado não existe.")

        ids_unicos = list(dict.fromkeys(dados.technology_ids))
        tecnologias = self.tecnologias.get_by_ids(ids_unicos)
        if len(tecnologias) != len(ids_unicos):
            raise NotFoundError("Uma ou mais tecnologias informadas não existem.")

        projeto = Project(
            title=dados.title,
            description=dados.description,
            repository_url=str(dados.repository_url),
            profile_id=dados.profile_id,
            technologies=tecnologias,
        )
        return self.projetos.create(projeto)

    def listar(self, technology: str | None, page: int, size: int) -> dict:
        if page < 1:
            raise BadRequestError("O parâmetro page deve ser maior ou igual a 1.")
        if size < 1 or size > TAMANHO_MAXIMO:
            raise BadRequestError("O parâmetro size deve estar entre 1 e 100.")

        tecnologia = technology.strip() if technology else None
        if tecnologia == "":
            tecnologia = None

        itens, total = self.projetos.listar_paginado(tecnologia, page, size)
        paginas = math.ceil(total / size) if total else 0
        return {
            "items": itens,
            "page": page,
            "size": size,
            "total": total,
            "pages": paginas,
        }

    def registrar_upvote(self, project_id: int) -> Project:
        projeto = self.projetos.get_by_id(project_id)
        if projeto is None:
            raise NotFoundError("Projeto não encontrado.")
        projeto.upvotes = int(projeto.upvotes or 0) + 1
        return self.projetos.atualizar(projeto)


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.projetos = ProjectRepository(db)
        self.feedbacks = FeedbackRepository(db)

    def criar(self, project_id: int, dados: FeedbackCreate) -> dict:
        projeto = self.projetos.get_by_id(project_id)
        if projeto is None:
            raise NotFoundError("Projeto não encontrado.")
        if dados.rating < 1 or dados.rating > 5:
            raise BadRequestError("A nota deve estar entre 1 e 5.")

        comentario = dados.comment.strip()
        if not comentario:
            raise BadRequestError("O comentário não pode ser vazio.")

        autor = (dados.author_name or "").strip() or "Anônimo"
        feedback = Feedback(
            author_name=autor,
            message=comentario,
            rating=dados.rating,
            project_id=projeto.id,
        )
        self.feedbacks.add(feedback)
        projeto.average_rating = calcular_media(
            self.feedbacks.listar_notas(projeto.id)
        )
        self.projetos.atualizar(projeto)
        self.db.refresh(feedback)
        return {
            "id": feedback.id,
            "author_name": feedback.author_name,
            "comment": feedback.message,
            "rating": feedback.rating,
            "project_id": feedback.project_id,
            "average_rating": projeto.average_rating,
        }
