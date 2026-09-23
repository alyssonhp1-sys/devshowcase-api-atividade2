# DevShowcase API

API REST acadêmica para cadastrar o perfil de um desenvolvedor, as tecnologias utilizadas e os projetos do portfólio.

Não há interface web nem autenticação. As requisições podem ser feitas pela documentação interativa em `/docs` ou por um cliente HTTP.

## Objetivo

Implementar um backend REST com persistência em SQLite, contendo:

- cadastro e consulta de perfil;
- cadastro e listagem de tecnologias;
- cadastro e listagem de projetos;
- relacionamentos 1:N e N:N;
- DTOs de entrada e saída com validação.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Entidades

- **Profile:** id, name, bio, github_url, linkedin_url
- **Project:** id, title, description, repository_url, profile_id
- **Technology:** id, name
- **Feedback:** id, author_name, message, project_id

A entidade Feedback faz parte da modelagem e do banco de dados. Esta entrega não possui endpoints de feedback.

## Relacionamentos

- Profile 1:N Project
- Project N:N Technology (tabela associativa `project_technologies`)
- Project 1:N Feedback

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/api/profiles` | Cadastra um perfil |
| GET | `/api/profiles/{id}` | Busca um perfil pelo ID |
| POST | `/api/technologies` | Cadastra uma tecnologia |
| GET | `/api/technologies` | Lista as tecnologias |
| POST | `/api/projects` | Cadastra um projeto |
| GET | `/api/projects` | Lista os projetos |

Não há rota na raiz (`/`). A documentação da API fica em `/docs`.

## Como instalar

É necessário ter o Python 3 instalado.

No PowerShell, na pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se a ativação do ambiente virtual for bloqueada, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Em seguida, ative o ambiente novamente.

## Como executar

Com o ambiente virtual ativado:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

O arquivo SQLite `devshowcase.db` é criado na primeira execução, na pasta do projeto.

## Acesso ao /docs

Com a API em execução:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI: http://127.0.0.1:8000/openapi.json

## Estrutura

```text
DevShowcaseAPI/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── repositories.py
│   └── routers/
│       ├── profiles.py
│       ├── technologies.py
│       └── projects.py
├── requirements.txt
├── DevShowcase_API.postman_collection.json
├── .gitignore
└── README.md
```

A collection `DevShowcase_API.postman_collection.json` pode ser importada no Postman para testar os endpoints.
