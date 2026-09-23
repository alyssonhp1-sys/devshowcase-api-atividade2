import os
import tempfile
from pathlib import Path

_DIRETORIO = tempfile.mkdtemp(prefix="devshowcase_test_")
_ARQUIVO = Path(_DIRETORIO) / "teste.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_ARQUIVO.as_posix()}"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

_BANCO_PRINCIPAL = Path("devshowcase.db").resolve()
assert _ARQUIVO.resolve() != _BANCO_PRINCIPAL
assert "devshowcase.db" not in str(engine.url)


@pytest.fixture(autouse=True)
def banco_isolado():
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


@pytest.fixture
def client(banco_isolado):
    with TestClient(app) as cliente:
        yield cliente
