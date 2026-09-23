from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import Feedback, Profile, Project, Technology


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, profile: Profile) -> Profile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_by_id(self, profile_id: int) -> Profile | None:
        return self.db.get(Profile, profile_id)


class TechnologyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, technology: Technology) -> Technology:
        self.db.add(technology)
        self.db.commit()
        self.db.refresh(technology)
        return technology

    def get_all(self) -> list[Technology]:
        return self.db.query(Technology).order_by(Technology.id).all()

    def get_by_name(self, name: str) -> Technology | None:
        return self.db.query(Technology).filter(Technology.name == name).first()

    def get_by_ids(self, technology_ids: list[int]) -> list[Technology]:
        if not technology_ids:
            return []
        ids_unicos = list(set(technology_ids))
        return self.db.query(Technology).filter(Technology.id.in_(ids_unicos)).all()


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return self.get_by_id(project.id)

    def get_by_id(self, project_id: int) -> Project | None:
        return (
            self.db.query(Project)
            .options(selectinload(Project.technologies))
            .filter(Project.id == project_id)
            .first()
        )

    def get_all(self) -> list[Project]:
        return (
            self.db.query(Project)
            .options(selectinload(Project.technologies))
            .order_by(Project.id)
            .all()
        )

    def atualizar(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return self.get_by_id(project.id)

    def listar_paginado(
        self, tecnologia: str | None, page: int, size: int
    ) -> tuple[list[Project], int]:
        consulta = self.db.query(Project).options(selectinload(Project.technologies))
        if tecnologia:
            consulta = consulta.filter(
                Project.technologies.any(
                    func.lower(Technology.name) == tecnologia.lower()
                )
            )
        total = consulta.count()
        itens = (
            consulta.order_by(Project.id)
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return itens, total


class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        self.db.flush()
        return feedback

    def listar_notas(self, project_id: int) -> list[int]:
        linhas = (
            self.db.query(Feedback.rating)
            .filter(Feedback.project_id == project_id)
            .all()
        )
        return [linha[0] for linha in linhas]
