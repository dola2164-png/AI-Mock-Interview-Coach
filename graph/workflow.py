from langgraph.graph import StateGraph, END
from graph.state import InterviewState
from agents.interviewer import run_interviewer_agent
from agents.evaluator import run_evaluator_agent
from agents.decision import run_decision_agent
from agents.coach import run_coach_agent

def node_interviewer(state: InterviewState) -> dict:
    """Interviewer Agent Node: Generates the next question."""
    latest_dec = state.get("latest_decision", {})
    action_directive = latest_dec.get("action", "move_next_topic")

    result = run_interviewer_agent(
        target_role=state["target_role"],
        resume_snippet=state.get("resume_snippet", ""),
        interview_type=state["interview_type"],
        current_difficulty=state["current_difficulty"],
        decision_action=action_directive,
        question_history=state.get("question_history", []),
        api_key=state.get("api_key")
    )

    return {
        "latest_question": result["question"],
        "latest_question_reason": result["reason"],
        "current_difficulty": result.get("difficulty", state["current_difficulty"])
    }

def node_evaluator(state: InterviewState) -> dict:
    """Evaluator Agent Node: Evaluates the candidate's answer."""
    evaluation = run_evaluator_agent(
        target_role=state["target_role"],
        question=state["latest_question"],
        answer=state["latest_answer"],
        api_key=state.get("api_key")
    )
    return {"latest_evaluation": evaluation}

def node_decision(state: InterviewState) -> dict:
    """Decision Agent Node: Analyzes evaluation and decides next step & difficulty."""
    current_idx = state.get("current_question_index", 0) + 1
    max_q = state.get("max_questions", 5)

    decision = run_decision_agent(
        current_round=current_idx,
        max_rounds=max_q,
        current_difficulty=state["current_difficulty"],
        evaluation=state["latest_evaluation"],
        api_key=state.get("api_key")
    )

    # Save completed round to question_history
    round_record = {
        "round": current_idx,
        "question": state["latest_question"],
        "reason": state.get("latest_question_reason", ""),
        "answer": state["latest_answer"],
        "difficulty": state["current_difficulty"],
        "evaluation": state["latest_evaluation"],
        "decision": decision
    }

    history = list(state.get("question_history", []))
    history.append(round_record)

    next_difficulty = decision.get("target_difficulty", state["current_difficulty"])

    return {
        "current_question_index": current_idx,
        "question_history": history,
        "latest_decision": decision,
        "current_difficulty": next_difficulty
    }

def node_coach(state: InterviewState) -> dict:
    """Coach Agent Node: Generates final markdown report."""
    report = run_coach_agent(
        target_role=state["target_role"],
        interview_type=state["interview_type"],
        resume_snippet=state.get("resume_snippet", ""),
        question_history=state.get("question_history", []),
        api_key=state.get("api_key")
    )
    return {
        "coaching_report": report,
        "is_complete": True
    }

def route_after_decision(state: InterviewState) -> str:
    """Routing condition: continue to interviewer or finalize with coach."""
    if state["current_question_index"] >= state["max_questions"]:
        return "coach"
    return "interviewer"

def build_interview_graph():
    """Builds and compiles the LangGraph StateGraph."""
    workflow = StateGraph(InterviewState)

    workflow.add_node("interviewer", node_interviewer)
    workflow.add_node("evaluator", node_evaluator)
    workflow.add_node("decision", node_decision)
    workflow.add_node("coach", node_coach)

    workflow.set_entry_point("interviewer")

    workflow.add_edge("interviewer", END) # Pauses for user answer
    workflow.add_edge("evaluator", "decision")
    
    workflow.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "interviewer": "interviewer",
            "coach": "coach"
        }
    )
    
    workflow.add_edge("coach", END)

    return workflow.compile()
