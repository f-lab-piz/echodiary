from sqlalchemy import UniqueConstraint

from app.models import Base


def test_required_tables_exist() -> None:
    expected = {"personas", "diaries", "diary_personas", "entries"}
    actual = set(Base.metadata.tables.keys())

    assert expected.issubset(actual)


def test_diary_persona_unique_constraint_exists() -> None:
    table = Base.metadata.tables["diary_personas"]
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]

    assert any({"diary_id", "persona_id"} == {col.name for col in c.columns} for c in unique_constraints)


def test_entry_input_check_constraint_exists() -> None:
    table = Base.metadata.tables["entries"]
    check_sqltexts = [str(c.sqltext) for c in table.constraints if c.__class__.__name__ == "CheckConstraint"]

    assert any("input_keywords" in text and "input_text" in text for text in check_sqltexts)
