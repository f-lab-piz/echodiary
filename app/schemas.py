from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)


class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)


class PersonaCreate(BaseModel):
    account_id: str
    name: str = Field(min_length=1, max_length=100)
    tone: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)


class DiaryCreate(BaseModel):
    account_id: str
    title: str = Field(min_length=1, max_length=120)


class EntryGenerateRequest(BaseModel):
    diary_id: str
    persona_id: str
    input_keywords: str | None = None
    input_text: str | None = None


class EntrySaveRequest(BaseModel):
    draft: str = Field(min_length=1)
