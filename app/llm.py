import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

load_dotenv()


class DraftState(TypedDict):
    tone: str
    source: str
    draft: str


def _fallback_draft(*, tone: str, source: str) -> str:
    return f"[{tone}] {source}"


def _build_graph() -> StateGraph:
    workflow = StateGraph(DraftState)

    def compose_node(state: DraftState) -> DraftState:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        if not api_key or os.getenv("ECHODIARY_DISABLE_LLM") == "true":
            return {**state, "draft": _fallback_draft(tone=state["tone"], source=state["source"])}

        llm = ChatOpenAI(model=model, api_key=api_key, temperature=0.7, timeout=8, max_retries=0)
        try:
            response = llm.invoke(
                [
                    SystemMessage(content="너는 사용자의 메모를 자연스럽고 짧은 한국어 일기 문장으로 정리한다."),
                    HumanMessage(
                        content=(
                            f"톤: {state['tone']}\n"
                            f"입력: {state['source']}\n"
                            "요청: 4~6문장 분량의 자연스러운 한국어 일기 초안을 작성해줘."
                        )
                    ),
                ]
            )
        except Exception:  # noqa: BLE001
            return {**state, "draft": _fallback_draft(tone=state["tone"], source=state["source"])}

        content = (response.content or "").strip() if isinstance(response.content, str) else ""
        return {**state, "draft": content or _fallback_draft(tone=state["tone"], source=state["source"])}

    workflow.add_node("compose", compose_node)
    workflow.set_entry_point("compose")
    workflow.add_edge("compose", END)
    return workflow.compile()


_draft_graph = _build_graph()


def generate_diary_draft(*, tone: str, source: str) -> str:
    result = _draft_graph.invoke({"tone": tone, "source": source, "draft": ""})
    return result["draft"]
