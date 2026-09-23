import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLITE_LOCAL = "sqlite:///./devshowcase.db"


def resolver_database_url() -> str:
    """Usa DATABASE_URL quando existir. Sem a variável, permanece no SQLite local."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return SQLITE_LOCAL
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = resolver_database_url()

_argumentos_engine: dict = {}
if DATABASE_URL.startswith("sqlite"):
    _argumentos_engine["connect_args"] = {"check_same_thread": False}
else:
    _argumentos_engine["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **_argumentos_engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _adicionar_coluna_se_ausente(tabela: str, coluna: str, definicao: str) -> None:
    inspector = inspect(engine)
    if tabela not in inspector.get_table_names():
        return
    existentes = {item["name"] for item in inspector.get_columns(tabela)}
    if coluna in existentes:
        return
    with engine.begin() as conexao:
        conexao.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"))


def _atualizar_colunas_existentes() -> None:
    """Inclui colunas novas em bancos já criados, sem apagar os dados atuais."""
    _adicionar_coluna_se_ausente("projects", "upvotes", "INTEGER NOT NULL DEFAULT 0")
    _adicionar_coluna_se_ausente(
        "projects", "average_rating", "FLOAT NOT NULL DEFAULT 0"
    )
    _adicionar_coluna_se_ausente(
        "feedbacks", "rating", "INTEGER NOT NULL DEFAULT 0"
    )


def create_tables():
    from app import models  # noqa: F401 — registra as entidades no SQLAlchemy

    Base.metadata.create_all(bind=engine)
    _atualizar_colunas_existentes()
