from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


def _texto_obrigatorio(valor: str) -> str:
    texto = valor.strip() if valor is not None else ""
    if not texto:
        raise ValueError("não pode ser vazio")
    return texto


class ProfileCreate(BaseModel):
    name: str
    bio: str | None = None
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None

    @field_validator("name")
    @classmethod
    def validar_name(cls, valor: str) -> str:
        return _texto_obrigatorio(valor)

    @field_validator("bio")
    @classmethod
    def validar_bio(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None
    github_url: str | None
    linkedin_url: str | None


class TechnologyCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validar_name(cls, valor: str) -> str:
        return _texto_obrigatorio(valor)


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    repository_url: HttpUrl
    profile_id: int = Field(..., gt=0)
    technology_ids: list[int] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validar_title(cls, valor: str) -> str:
        return _texto_obrigatorio(valor)

    @field_validator("description")
    @classmethod
    def validar_description(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None

    @field_validator("technology_ids")
    @classmethod
    def validar_technology_ids(cls, valor: list[int]) -> list[int]:
        for item in valor:
            if item <= 0:
                raise ValueError("os IDs das tecnologias devem ser maiores que zero")
        return valor


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    repository_url: str | None
    profile_id: int
    upvotes: int
    average_rating: float
    technologies: list[TechnologyResponse]


class ProjectPage(BaseModel):
    items: list[ProjectResponse]
    page: int
    size: int
    total: int
    pages: int


class FeedbackCreate(BaseModel):
    rating: int = Field(..., description="Nota de 1 a 5.")
    comment: str = Field(..., description="Comentário obrigatório e não vazio.")
    author_name: str | None = Field(
        default=None,
        description="Nome de quem enviou o feedback. Opcional.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rating": 5,
                "comment": "Excelente projeto, muito bem estruturado.",
            }
        }
    )


class FeedbackResponse(BaseModel):
    id: int
    author_name: str
    comment: str
    rating: int
    project_id: int
    average_rating: float


class ErrorResponse(BaseModel):
    status: int
    error: str
    message: str
