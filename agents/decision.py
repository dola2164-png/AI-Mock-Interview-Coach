import os
import json
import re
from config import get_llm

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "decision.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_json_string(content: str) -> str:
    content = content.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return content

def run_decision_agent(
    current_round: int,
    max_rounds: int,
    current_difficulty: str,
    evaluation: dict,
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile"
) -> dict:
    llm = get_llm(api_key=api_key, model_name=model_name, temperature=0.3)
    prompt_template = load_prompt()

    eval_json_str = json.dumps(evaluation, indent=2)

    formatted_prompt = prompt_template.format(
        current_round=current_round,
        max_rounds=max_rounds,
        current_difficulty=current_difficulty,
        evaluation_json=eval_json_str
    )

    response = llm.invoke(formatted_prompt)
    raw_text = response.content if hasattr(response, "content") else str(response)
    
    cleaned = clean_json_string(raw_text)
    try:
        data = json.loads(cleaned)
        action = data.get("action", "move_next_topic")
        target_diff = data.get("target_difficulty", current_difficulty)
        reasoning = data.get("reasoning", "Adaptive progression decision.")
        return {
            "action": action,
            "target_difficulty": target_diff,
            "reasoning": reasoning
        }
    except Exception:
        if evaluation.get("follow_up_needed"):
            return {
                "action": "probe_deeper",
                "target_difficulty": current_difficulty,
                "reasoning": "Follow up needed based on evaluation."
            }
        return {
            "action": "move_next_topic",
            "target_difficulty": current_difficulty,
            "reasoning": "Moving to next interview topic."
        }
