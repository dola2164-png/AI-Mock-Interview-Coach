from typing import TypedDict, List, Dict, Optional

class InterviewState(TypedDict):
    target_role: str
    resume_snippet: str
    interview_type: str
    max_questions: int
    current_question_index: int
    current_difficulty: str
    question_history: List[Dict]
    latest_question: str
    latest_question_reason: str
    latest_answer: str
    latest_evaluation: Dict
    latest_decision: Dict
    coaching_report: str
    is_complete: bool
    api_key: Optional[str]
