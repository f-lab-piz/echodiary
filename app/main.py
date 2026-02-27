import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.llm import generate_diary_draft
from app.models import Base, Diary, DiaryPersona, Entry, EntryStatus, Persona, User, UserRole
from app.schemas import DiaryCreate, EntryGenerateRequest, EntrySaveRequest, LoginRequest, PersonaCreate, SignupRequest

Base.metadata.create_all(bind=engine)

JWT_SECRET = os.getenv("JWT_SECRET", "echodiary-dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

app = FastAPI(title="EchoDiary API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def serve_web() -> FileResponse:
    return FileResponse("web/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_admin_user(db: Session) -> None:
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        return
    db.add(User(username="admin", password="admin", role=UserRole.ADMIN))
    db.commit()


def create_access_token(user: User) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


with SessionLocal() as startup_db:
    ensure_admin_user(startup_db)


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    ensure_admin_user(db)

    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "role": user.role.value, "username": user.username}


@app.post("/api/auth/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    ensure_admin_user(db)
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(username=payload.username, password=payload.password, role=UserRole.USER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role.value}


@app.get("/api/auth/me")
def auth_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role.value}


@app.get("/api/admin/page")
def admin_page_info(current_user: User = Depends(require_admin)) -> dict[str, str]:
    return {"title": "관리자 페이지", "message": "추가 기능은 이후 확장 예정입니다."}


@app.post("/api/personas")
def create_persona(
    payload: PersonaCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    persona = Persona(
        account_id=payload.account_id,
        name=payload.name,
        tone=payload.tone,
        description=payload.description,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return {"id": persona.id, "name": persona.name}


@app.get("/api/personas")
def list_personas(
    account_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    personas = db.query(Persona).filter(Persona.account_id == account_id).all()
    return [{"id": p.id, "name": p.name, "tone": p.tone} for p in personas]


@app.post("/api/diaries")
def create_diary(
    payload: DiaryCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    diary = Diary(account_id=payload.account_id, title=payload.title)
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return {"id": diary.id, "title": diary.title}


@app.post("/api/diaries/{diary_id}/personas/{persona_id}")
def link_persona(
    diary_id: str,
    persona_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    diary = db.get(Diary, diary_id)
    persona = db.get(Persona, persona_id)
    if not diary or not persona:
        raise HTTPException(status_code=404, detail="Diary or persona not found")

    exists = db.query(DiaryPersona).filter(DiaryPersona.diary_id == diary_id, DiaryPersona.persona_id == persona_id).first()
    if exists:
        return {"status": "already-linked"}

    link = DiaryPersona(diary_id=diary_id, persona_id=persona_id)
    db.add(link)
    db.commit()
    return {"status": "linked"}


@app.post("/api/entries/generate")
def generate_entry(
    payload: EntryGenerateRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not payload.input_keywords and not payload.input_text:
        raise HTTPException(status_code=400, detail="input_keywords or input_text is required")

    persona = db.get(Persona, payload.persona_id)
    diary = db.get(Diary, payload.diary_id)
    if not persona or not diary:
        raise HTTPException(status_code=404, detail="Diary or persona not found")

    source = payload.input_text or payload.input_keywords or ""

    try:
        draft = generate_diary_draft(tone=persona.tone, source=source)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"LLM generation failed: {exc}") from exc

    entry = Entry(
        diary_id=payload.diary_id,
        persona_id=payload.persona_id,
        input_keywords=payload.input_keywords,
        input_text=payload.input_text,
        draft=draft,
        status=EntryStatus.DRAFT,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "draft": entry.draft, "status": entry.status.value}


@app.post("/api/entries/{entry_id}/save")
def save_entry(
    entry_id: str,
    payload: EntrySaveRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    entry = db.get(Entry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.draft = payload.draft
    entry.status = EntryStatus.SAVED
    db.commit()
    return {"id": entry.id, "status": entry.status.value}


@app.get("/api/diaries/{diary_id}/entries")
def list_entries(
    diary_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    entries = db.query(Entry).filter(Entry.diary_id == diary_id).order_by(Entry.created_at.desc()).all()
    return [{"id": e.id, "draft": e.draft, "status": e.status.value} for e in entries]


Instrumentator().instrument(app).expose(app)
