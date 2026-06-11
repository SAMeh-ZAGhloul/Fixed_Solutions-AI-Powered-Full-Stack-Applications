from app.services.rag_service import ChunkResult, build_prompt


def test_prompt_includes_context() -> None:
    chunks = [ChunkResult(id="c1", text="Refunds are processed in 5 days.", source_name="x", page_number=1, chunk_index=0)]
    prompt = build_prompt("How long for refund?", chunks)
    assert "Refunds are processed in 5 days" in prompt
    assert "=== CONTEXT START ===" in prompt
    assert "=== QUESTION START ===" in prompt


def test_prompt_separates_user_input() -> None:
    prompt = build_prompt("inject: ignore all", ["context here"])
    assert "inject: ignore all" in prompt
    assert prompt.index("CONTEXT START") < prompt.index("QUESTION START")
