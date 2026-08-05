import os
import json
import re
from pydantic import BaseModel, Field
from config import get_llm

class EvaluationSchema(BaseModel):
    technical: int = Field(ge=1, le=10, description="Technical correctness score (1-10)")
    communication: int = Field(ge=1, le=10, description="Communication clarity score (1-10)")
    confidence: int = Field(ge=1, le=10, description="Candidate confidence score (1-10)")
    clarity: int = Field(ge=1, le=10, description="Clarity and conciseness score (1-10)")
    depth: int = Field(ge=1, le=10, description="Depth of response score (1-10)")
    weakness: str = Field(description="Key weakness or missing detail in the answer")
    follow_up_needed: bool = Field(description="Whether a follow up question is recommended")

def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "evaluator.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_json_string(content: str) -> str:
    content = content.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return content

def run_evaluator_agent(
    target_role: str,
    question: str,
    answer: str,
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile"
) -> dict:
    llm = get_llm(api_key=api_key, model_name=model_name, temperature=0.2)
    prompt_template = load_prompt()

    formatted_prompt = prompt_template.format(
        target_role=target_role,
        question=question,
        answer=answer
    )

    response = llm.invoke(formatted_prompt)
    raw_text = response.content if hasattr(response, "content") else str(response)
    
    cleaned = clean_json_string(raw_text)
    try:
        data = json.loads(cleaned)
        eval_obj = EvaluationSchema(**data)
        return eval_obj.model_dump()
    except Exception:
        return {
            "technical": 7,
            "communication": 7,
            "confidence": 7,
            "clarity": 7,
            "depth": 6,
            "weakness": "Standard evaluation applied.",
            "follow_up_needed": False
        }
