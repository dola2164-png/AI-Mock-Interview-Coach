import os
import json
import re
from config import get_llm

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "interviewer.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_json_string(content: str) -> str:
    """Removes markdown backticks and extracts pure JSON text."""
    content = content.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return content

def run_interviewer_agent(
    target_role: str,
    resume_snippet: str,
    interview_type: str,
    current_difficulty: str,
    decision_action: str,
    question_history: list,
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile"
) -> dict:
    llm = get_llm(api_key=api_key, model_name=model_name, temperature=0.7)
    prompt_template = load_prompt()

    # Format question history into readable string
    history_str = ""
    if not question_history:
        history_str = "No questions asked yet. This is the start of the interview."
    else:
        for idx, item in enumerate(question_history, 1):
            history_str += f"\nRound {idx}:\nQuestion: {item.get('question')}\nAnswer: {item.get('answer')}\n"

    formatted_prompt = prompt_template.format(
        target_role=target_role,
        resume_snippet=resume_snippet or "None provided",
        interview_type=interview_type,
        current_difficulty=current_difficulty,
        decision_action=decision_action or "move_next_topic",
        question_history=history_str
    )

    response = llm.invoke(formatted_prompt)
    raw_text = response.content if hasattr(response, "content") else str(response)
    
    cleaned = clean_json_string(raw_text)
    try:
        data = json.loads(cleaned)
        return {
            "question": data.get("question", raw_text),
            "difficulty": data.get("difficulty", current_difficulty),
            "reason": data.get("reason", "Question selected based on candidate profile.")
        }
    except Exception:
        return {
            "question": raw_text,
            "difficulty": current_difficulty,
            "reason": "Adaptive selection based on candidate state."
        }
