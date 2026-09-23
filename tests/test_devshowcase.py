from app.services import calcular_media

PERFIL = {
    "name": "Alysson Moura Pinheiro",
    "bio": "Desenvolvedor participante do projeto DevShowcase API",
    "github_url": "https://github.com/alyssonhp1-sys",
    "linkedin_url": "https://www.linkedin.com",
}

PROJETO = {
    "title": "DevShowcase API",
    "description": "API para apresentação de perfis e projetos de desenvolvedores.",
    "repository_url": "https://github.com/alyssonhp1-sys/devshowcase-api",
}


def _criar_perfil(client) -> dict:
    resposta = client.post("/api/profiles", json=PERFIL)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _criar_tecnologia(client, nome: str) -> dict:
    resposta = client.post("/api/technologies", json={"name": nome})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _criar_projeto(client, profile_id: int, technology_ids: list[int], titulo: str) -> dict:
    resposta = client.post(
        "/api/projects",
        json={
            **PROJETO,
            "title": titulo,
            "profile_id": profile_id,
            "technology_ids": technology_ids,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _preparar_projeto(client, tecnologias: list[str] | None = None) -> dict:
    perfil = _criar_perfil(client)
    nomes = tecnologias or ["Python", "FastAPI"]
    ids = [_criar_tecnologia(client, nome)["id"] for nome in nomes]
    projeto = _criar_projeto(client, perfil["id"], ids, "DevShowcase API")
    return {"perfil": perfil, "technology_ids": ids, "projeto": projeto}


def _feedback(client, project_id: int, rating: int, comment: str = "Muito bom."):
    return client.post(
        f"/api/projects/{project_id}/feedbacks",
        json={"rating": rating, "comment": comment},
    )


def test_cria_feedback_valido(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 4, "  Projeto bem organizado.  ")
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["rating"] == 4
    assert corpo["comment"] == "Projeto bem organizado."
    assert corpo["author_name"] == "Anônimo"
    assert corpo["project_id"] == projeto["id"]
    assert corpo["id"] >= 1
    assert corpo["average_rating"] == 4.0


def test_aceita_nota_1(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 1, "Nota mínima.")
    assert resposta.status_code == 201
    assert resposta.json()["rating"] == 1


def test_aceita_nota_5(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 5, "Nota máxima.")
    assert resposta.status_code == 201
    assert resposta.json()["rating"] == 5


def test_rejeita_nota_menor_que_1(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 0, "Nota inválida.")
    assert resposta.status_code == 400
    assert resposta.json()["message"] == "A nota deve estar entre 1 e 5."


def test_rejeita_nota_maior_que_5(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 6, "Nota inválida.")
    assert resposta.status_code == 400
    assert resposta.json()["message"] == "A nota deve estar entre 1 e 5."


def test_rejeita_comentario_vazio(client):
    projeto = _preparar_projeto(client)["projeto"]
    vazio = _feedback(client, projeto["id"], 5, "")
    espacos = _feedback(client, projeto["id"], 5, "   ")
    assert vazio.status_code == 400
    assert espacos.status_code == 400
    assert vazio.json()["message"] == "O comentário não pode ser vazio."
    assert espacos.json()["message"] == "O comentário não pode ser vazio."


def test_feedback_projeto_inexistente(client):
    resposta = _feedback(client, 9999, 5, "Projeto inexistente.")
    assert resposta.status_code == 404
    assert resposta.json()["message"] == "Projeto não encontrado."


def test_calcula_media_do_primeiro_feedback(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 5, "Excelente projeto.")
    assert resposta.status_code == 201
    assert resposta.json()["average_rating"] == 5.0


def test_atualiza_media_apos_segundo_feedback(client):
    projeto = _preparar_projeto(client)["projeto"]
    primeiro = _feedback(client, projeto["id"], 5, "Excelente projeto.")
    segundo = _feedback(client, projeto["id"], 3, "Bom projeto, com pontos a melhorar.")
    assert primeiro.status_code == 201
    assert segundo.status_code == 201
    assert primeiro.json()["average_rating"] == 5.0
    assert segundo.json()["average_rating"] == 4.0

    listagem = client.get("/api/projects")
    assert listagem.status_code == 200
    salvos = listagem.json()["items"]
    assert len(salvos) == 1
    assert salvos[0]["average_rating"] == 4.0


def test_media_vazia_nao_divide_por_zero():
    assert calcular_media([]) == 0.0


def test_primeiro_upvote_de_zero_para_um(client):
    projeto = _preparar_projeto(client)["projeto"]
    assert projeto["upvotes"] == 0
    resposta = client.put(f"/api/projects/{projeto['id']}/upvote")
    assert resposta.status_code == 200
    assert resposta.json()["upvotes"] == 1


def test_segundo_upvote_de_um_para_dois(client):
    projeto = _preparar_projeto(client)["projeto"]
    primeiro = client.put(f"/api/projects/{projeto['id']}/upvote")
    segundo = client.put(f"/api/projects/{projeto['id']}/upvote")
    assert primeiro.json()["upvotes"] == 1
    assert segundo.status_code == 200
    assert segundo.json()["upvotes"] == 2

    listagem = client.get("/api/projects")
    assert listagem.json()["items"][0]["upvotes"] == 2


def test_upvote_projeto_inexistente_retorna_404(client):
    resposta = client.put("/api/projects/9999/upvote")
    assert resposta.status_code == 404
    assert resposta.json() == {
        "status": 404,
        "error": "Not Found",
        "message": "Projeto não encontrado.",
    }


def test_lista_projetos_sem_filtro(client):
    _preparar_projeto(client)
    resposta = client.get("/api/projects")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["page"] == 1
    assert corpo["size"] == 10
    assert corpo["total"] == 1
    assert corpo["pages"] == 1
    assert len(corpo["items"]) == 1
    assert corpo["items"][0]["title"] == "DevShowcase API"


def test_filtra_projetos_por_tecnologia(client):
    perfil = _criar_perfil(client)
    python_id = _criar_tecnologia(client, "Python")["id"]
    java_id = _criar_tecnologia(client, "Java")["id"]
    projeto_python = _criar_projeto(client, perfil["id"], [python_id], "API Python")
    projeto_java = _criar_projeto(client, perfil["id"], [java_id], "API Java")

    resposta = client.get("/api/projects", params={"technology": "Python"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    ids = [item["id"] for item in corpo["items"]]
    assert ids == [projeto_python["id"]]
    assert projeto_java["id"] not in ids
    assert corpo["total"] == 1


def test_filtro_tecnologia_sem_resultados(client):
    _preparar_projeto(client)
    resposta = client.get("/api/projects", params={"technology": "Ruby"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["items"] == []
    assert corpo["total"] == 0
    assert corpo["pages"] == 0


def test_paginacao_pagina_1(client):
    perfil = _criar_perfil(client)
    tecnologia_id = _criar_tecnologia(client, "Python")["id"]
    for indice in range(1, 4):
        _criar_projeto(client, perfil["id"], [tecnologia_id], f"Projeto {indice}")

    resposta = client.get("/api/projects", params={"page": 1, "size": 2})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["page"] == 1
    assert corpo["size"] == 2
    assert corpo["total"] == 3
    assert corpo["pages"] == 2
    assert len(corpo["items"]) == 2
    assert [item["title"] for item in corpo["items"]] == ["Projeto 1", "Projeto 2"]


def test_paginacao_outra_pagina(client):
    perfil = _criar_perfil(client)
    tecnologia_id = _criar_tecnologia(client, "Python")["id"]
    for indice in range(1, 4):
        _criar_projeto(client, perfil["id"], [tecnologia_id], f"Projeto {indice}")

    resposta = client.get("/api/projects", params={"page": 2, "size": 2})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["page"] == 2
    assert corpo["size"] == 2
    assert corpo["total"] == 3
    assert corpo["pages"] == 2
    assert len(corpo["items"]) == 1
    assert corpo["items"][0]["title"] == "Projeto 3"


def test_paginacao_parametros_invalidos(client):
    for parametros in ({"page": 0}, {"page": -1}, {"size": 0}, {"size": 101}):
        resposta = client.get("/api/projects", params=parametros)
        assert resposta.status_code == 400
        corpo = resposta.json()
        assert corpo["status"] == 400
        assert corpo["error"] == "Bad Request"
        assert "message" in corpo


def test_resposta_global_404(client):
    upvote = client.put("/api/projects/9999/upvote")
    perfil = client.get("/api/profiles/9999")
    for resposta in (upvote, perfil):
        assert resposta.status_code == 404
        corpo = resposta.json()
        assert set(corpo) == {"status", "error", "message"}
        assert corpo["status"] == 404
        assert corpo["error"] == "Not Found"
        assert "traceback" not in resposta.text.lower()
    assert upvote.json()["message"] == "Projeto não encontrado."
    assert perfil.json()["message"] == "Perfil não encontrado."


def test_resposta_400_padronizada(client):
    projeto = _preparar_projeto(client)["projeto"]
    resposta = _feedback(client, projeto["id"], 6, "Nota inválida para demonstrar o erro 400.")
    assert resposta.status_code == 400
    assert resposta.json() == {
        "status": 400,
        "error": "Bad Request",
        "message": "A nota deve estar entre 1 e 5.",
    }


def test_erro_de_validacao_padronizado(client):
    resposta = client.post("/api/projects/1/feedbacks", json={"rating": 5})
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["status"] == 422
    assert corpo["error"] == "Unprocessable Entity"
    assert "comment" in corpo["message"]
    assert "detail" not in corpo


def test_filtro_e_paginacao_combinados(client):
    perfil = _criar_perfil(client)
    python_id = _criar_tecnologia(client, "Python")["id"]
    java_id = _criar_tecnologia(client, "Java")["id"]
    for indice in range(1, 4):
        _criar_projeto(client, perfil["id"], [python_id], f"Python {indice}")
    _criar_projeto(client, perfil["id"], [java_id], "Somente Java")

    resposta = client.get(
        "/api/projects",
        params={"technology": "Python", "page": 1, "size": 2},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert corpo["pages"] == 2
    assert len(corpo["items"]) == 2
    assert all("Python" in item["title"] for item in corpo["items"])


def test_endpoints_atividade_1_continuam_funcionando(client):
    perfil = _criar_perfil(client)
    busca = client.get(f"/api/profiles/{perfil['id']}")
    assert busca.status_code == 200
    assert busca.json()["name"] == PERFIL["name"]
    assert busca.json()["github_url"] == PERFIL["github_url"]

    tecnologia = _criar_tecnologia(client, "Python")
    listagem_tecnologias = client.get("/api/technologies")
    assert listagem_tecnologias.status_code == 200
    assert any(item["name"] == "Python" for item in listagem_tecnologias.json())

    duplicada = client.post("/api/technologies", json={"name": "Python"})
    assert duplicada.status_code == 409
    assert duplicada.json()["error"] == "Conflict"

    projeto = _criar_projeto(client, perfil["id"], [tecnologia["id"]], "DevShowcase API")
    assert projeto["upvotes"] == 0
    assert projeto["average_rating"] == 0.0
    assert projeto["technologies"][0]["name"] == "Python"

    listagem = client.get("/api/projects")
    assert listagem.status_code == 200
    assert any(item["id"] == projeto["id"] for item in listagem.json()["items"])


def test_openapi_preserva_endpoints_e_documenta_atividade_2(client):
    resposta = client.get("/openapi.json")
    assert resposta.status_code == 200
    documento = resposta.json()
    caminhos = documento["paths"]
    for caminho in (
        "/api/profiles",
        "/api/profiles/{id}",
        "/api/technologies",
        "/api/projects",
        "/api/projects/{id}/feedbacks",
        "/api/projects/{id}/upvote",
    ):
        assert caminho in caminhos

    parametros = {item["name"] for item in caminhos["/api/projects"]["get"]["parameters"]}
    assert {"technology", "page", "size"} <= parametros
    assert "post" in caminhos["/api/projects/{id}/feedbacks"]
    assert "put" in caminhos["/api/projects/{id}/upvote"]
    assert "FeedbackCreate" in documento["components"]["schemas"]
    assert "ProjectPage" in documento["components"]["schemas"]

    docs = client.get("/docs")
    assert docs.status_code == 200
    assert "swagger-ui" in docs.text
    assert "/openapi.json" in docs.text


def test_sem_database_url_usa_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from app.database import SQLITE_LOCAL, resolver_database_url

    assert resolver_database_url() == SQLITE_LOCAL


def test_database_url_postgresql_usa_psycopg(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/devshowcase")
    from app.database import resolver_database_url

    assert resolver_database_url() == "postgresql+psycopg://localhost/devshowcase"


def test_database_url_postgres_legado_e_reescrito(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://localhost/devshowcase")
    from app.database import resolver_database_url

    assert resolver_database_url() == "postgresql+psycopg://localhost/devshowcase"
