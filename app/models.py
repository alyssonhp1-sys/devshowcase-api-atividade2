from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)

    # Relacionamento 1:N — um perfil possui vários projetos
    projects = relationship("Project", back_populates="profile")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    repository_url = Column(String, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    upvotes = Column(Integer, nullable=False, default=0, server_default="0")
    average_rating = Column(Float, nullable=False, default=0.0, server_default="0")

    # Relacionamento N:1 — um projeto pertence a um perfil
    profile = relationship("Profile", back_populates="projects")

    # Relacionamento N:N — um projeto usa várias tecnologias
    technologies = relationship(
        "Technology",
        secondary="project_technologies",
        back_populates="projects",
    )

    # Relacionamento 1:N — um projeto possui vários feedbacks
    feedbacks = relationship("Feedback", back_populates="project")


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # Relacionamento N:N — uma tecnologia pode aparecer em vários projetos
    projects = relationship(
        "Project",
        secondary="project_technologies",
        back_populates="technologies",
    )


class ProjectTechnology(Base):
    """Tabela associativa do relacionamento N:N entre Project e Technology."""

    __tablename__ = "project_technologies"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    technology_id = Column(Integer, ForeignKey("technologies.id"), primary_key=True)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Relacionamento N:1 — um feedback pertence a um projeto
    project = relationship("Project", back_populates="feedbacks")

    @property
    def comment(self) -> str:
        return self.message
