from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Diary, DiaryPersona, Entry, EntryStatus, Persona
from app.schemas import DiaryCreate, EntryGenerateRequest, EntrySaveRequest, PersonaCreate

Base.metadata.create_all(bind=engine)

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


@app.post("/api/personas")
def create_persona(payload: PersonaCreate, db: Session = Depends(get_db)) -> dict[str, str]:
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
def list_personas(account_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    personas = db.query(Persona).filter(Persona.account_id == account_id).all()
    return [{"id": p.id, "name": p.name, "tone": p.tone} for p in personas]


@app.post("/api/diaries")
def create_diary(payload: DiaryCreate, db: Session = Depends(get_db)) -> dict[str, str]:
    diary = Diary(account_id=payload.account_id, title=payload.title)
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return {"id": diary.id, "title": diary.title}


@app.post("/api/diaries/{diary_id}/personas/{persona_id}")
def link_persona(diary_id: str, persona_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
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
def generate_entry(payload: EntryGenerateRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    if not payload.input_keywords and not payload.input_text:
        raise HTTPException(status_code=400, detail="input_keywords or input_text is required")

    persona = db.get(Persona, payload.persona_id)
    diary = db.get(Diary, payload.diary_id)
    if not persona or not diary:
        raise HTTPException(status_code=404, detail="Diary or persona not found")

    source = payload.input_text or payload.input_keywords or ""
    draft = f"[{persona.tone}] {source}"

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
def save_entry(entry_id: str, payload: EntrySaveRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    entry = db.get(Entry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.draft = payload.draft
    entry.status = EntryStatus.SAVED
    db.commit()
    return {"id": entry.id, "status": entry.status.value}


@app.get("/api/diaries/{diary_id}/entries")
def list_entries(diary_id: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:
    entries = db.query(Entry).filter(Entry.diary_id == diary_id).order_by(Entry.created_at.desc()).all()
    return [{"id": e.id, "draft": e.draft, "status": e.status.value} for e in entries]


Instrumentator().instrument(app).expose(app)
