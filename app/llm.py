import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_diary_draft(*, tone: str, source: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 키가 없으면 로컬 폴백 문구를 사용한다.
    if not api_key:
        return f"[{tone}] {source}"

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": "너는 사용자의 메모를 자연스럽고 짧은 한국어 일기 문장으로 정리한다.",
            },
            {
                "role": "user",
                "content": f"톤: {tone}\n입력: {source}\n요청: 4~6문장 분량의 자연스러운 한국어 일기 초안을 작성해줘.",
            },
        ],
    )

    content = response.choices[0].message.content
    if not content:
        return f"[{tone}] {source}"
    return content.strip()
