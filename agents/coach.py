import os
from config import get_llm

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "coach.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def run_coach_agent(
    target_role: str,
    interview_type: str,
    resume_snippet: str,
    question_history: list,
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile"
) -> str:
    llm = get_llm(api_key=api_key, model_name=model_name, temperature=0.5)
    prompt_template = load_prompt()

    # Build full readable transcript
    transcript_blocks = []
    for idx, item in enumerate(question_history, 1):
        q = item.get("question", "")
        a = item.get("answer", "")
        eval_data = item.get("evaluation", {})
        dec_data = item.get("decision", {})
        
        block = f"""
### Round {idx}
**Question Asked ({item.get('difficulty', 'Medium')} Difficulty):** {q}
**Candidate Answer:** {a}

**Evaluator Metrics:**
- Technical: {eval_data.get('technical', 'N/A')}/10 | Communication: {eval_data.get('communication', 'N/A')}/10
- Confidence: {eval_data.get('confidence', 'N/A')}/10 | Clarity: {eval_data.get('clarity', 'N/A')}/10 | Depth: {eval_data.get('depth', 'N/A')}/10
- Key Weakness Identified: {eval_data.get('weakness', 'None')}

**Decision Agent Action:** {dec_data.get('action', 'N/A')} ({dec_data.get('reasoning', '')})
--------------------------------------------------
"""
        transcript_blocks.append(block)

    full_transcript_str = "\n".join(transcript_blocks)

    formatted_prompt = prompt_template.format(
        target_role=target_role,
        interview_type=interview_type,
        resume_snippet=resume_snippet or "None provided",
        full_transcript=full_transcript_str
    )

    response = llm.invoke(formatted_prompt)
    return response.content if hasattr(response, "content") else str(response)
