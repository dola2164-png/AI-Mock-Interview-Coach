import streamlit as st
import os
import json
from config import get_api_key
from agents.interviewer import run_interviewer_agent
from agents.evaluator import run_evaluator_agent
from agents.decision import run_decision_agent
from agents.coach import run_coach_agent

# Streamlit Page Config
st.set_page_config(
    page_title="AI Interview & Evaluation Platform | Enterprise Edition",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Enable Text Copying Without Developer Shortcut Conflicts */
    div, p, span, h1, h2, h3, h4, code, pre {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Header Card */
    .enterprise-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .enterprise-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .enterprise-subtitle {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 4px;
        font-weight: 400;
    }

    /* Metric Containers */
    .metric-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 18px;
        text-align: left;
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #38bdf8;
        margin-top: 4px;
    }

    /* Score Progress Bars */
    .score-bar-bg {
        background-color: #334155;
        border-radius: 4px;
        height: 8px;
        width: 100%;
        overflow: hidden;
        margin-top: 4px;
    }
    .score-bar-fill {
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
        height: 100%;
        border-radius: 4px;
    }

    /* Status Pill */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #1e1b4b;
        color: #818cf8;
        border: 1px solid #4338ca;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #4338ca 100%);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "max_questions" not in st.session_state:
    st.session_state.max_questions = 5
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Medium"
if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "latest_question" not in st.session_state:
    st.session_state.latest_question = ""
if "latest_question_reason" not in st.session_state:
    st.session_state.latest_question_reason = ""
if "latest_evaluation" not in st.session_state:
    st.session_state.latest_evaluation = None
if "latest_decision" not in st.session_state:
    st.session_state.latest_decision = None
if "coaching_report" not in st.session_state:
    st.session_state.coaching_report = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Configuration
st.sidebar.markdown("### ⚙️ Environment & API")

# Streamlit Cloud Secrets or Environment Variable
env_key = ""
try:
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        env_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not env_key:
    env_key = os.getenv("GROQ_API_KEY", "")

if env_key and env_key.strip():
    st.sidebar.success("🔒 API Key Loaded from Secrets / Environment")
    api_key_input = st.sidebar.text_input(
        "Override Key (Optional)",
        value="",
        type="password",
        help="Credentials loaded securely. Provide text to override."
    )
else:
    st.sidebar.warning("API Key required. Set GROQ_API_KEY in Streamlit Secrets, .env, or below.")
    api_key_input = st.sidebar.text_input(
        "Groq API Key",
        value="",
        type="password",
        placeholder="gsk_••••••••••••••••"
    )

api_key = get_api_key(api_key_input)

model_name = st.sidebar.selectbox(
    "Orchestration Model",
    options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    index=0
)

st.sidebar.divider()
st.sidebar.markdown("### 📋 Candidate Profile")

target_role = st.sidebar.text_input("Target Role / Position", value="Frontend Engineer Intern")
interview_type = st.sidebar.selectbox("Assessment Focus Area", options=["Technical", "Behavioral", "Case Study", "Mixed"], index=3)
max_questions = st.sidebar.slider("Assessment Rounds", min_value=5, max_value=7, value=5)
resume_snippet = st.sidebar.text_area("Candidate Resume / Profile Summary (Optional)", height=120, placeholder="Paste candidate profile or key technical competencies...")

start_button = st.sidebar.button("Initialize Assessment", use_container_width=True)

if start_button:
    if not api_key:
        st.sidebar.error("Valid Groq API Key required to initialize candidate assessment.")
    else:
        st.session_state.interview_started = True
        st.session_state.interview_complete = False
        st.session_state.current_question_index = 0
        st.session_state.max_questions = max_questions
        st.session_state.current_difficulty = "Medium"
        st.session_state.question_history = []
        st.session_state.messages = []
        st.session_state.latest_evaluation = None
        st.session_state.latest_decision = None
        st.session_state.coaching_report = ""
        
        with st.spinner("Initializing Multi-Agent Interviewer Node..."):
            res = run_interviewer_agent(
                target_role=target_role,
                resume_snippet=resume_snippet,
                interview_type=interview_type,
                current_difficulty="Medium",
                decision_action="move_next_topic",
                question_history=[],
                api_key=api_key,
                model_name=model_name
            )
            st.session_state.latest_question = res["question"]
            st.session_state.latest_question_reason = res["reason"]
            st.session_state.current_difficulty = res.get("difficulty", "Medium")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Question 1 ({st.session_state.current_difficulty} Difficulty):**\n\n{res['question']}"
            })
        st.rerun()

# Main Enterprise Header
st.markdown("""
<div class="enterprise-header">
    <div class="enterprise-title">AI Interview & Competency Evaluation Platform</div>
    <div class="enterprise-subtitle">Enterprise Multi-Agent Candidate Assessment & Adaptive Orchestration Engine</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.interview_started:
    st.info("Select target role and click **Initialize Assessment** in the sidebar control panel to begin.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**1. Interviewer Agent**")
        st.caption("Generates role-tailored technical & behavioral interview prompts.")
    with c2:
        st.markdown("**2. Evaluator Agent**")
        st.caption("Structured JSON scoring across 5 technical & clarity dimensions.")
    with c3:
        st.markdown("**3. Decision Agent**")
        st.caption("Adaptive routing: deeper technical probing vs. difficulty scaling.")
    with c4:
        st.markdown("**4. Coach Agent**")
        st.caption("Synthesizes transcript into an executive competency report.")

else:
    # Live Assessment Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Target Position</div>
            <div class="metric-value">{target_role}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Assessment Progress</div>
            <div class="metric-value">Round {min(st.session_state.current_question_index + 1, st.session_state.max_questions)} / {st.session_state.max_questions}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Current Difficulty</div>
            <div class="metric-value">{st.session_state.current_difficulty}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Assessment Engine</div>
            <div class="metric-value">Groq (Llama 3.3 70B)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layout: Live Session & Multi-Agent Diagnostics Panel
    chat_col, diag_col = st.columns([1.65, 1.0])

    with chat_col:
        st.subheader("Candidate Session")
        
        # Display Message History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Candidate Answer Input
        if not st.session_state.interview_complete:
            user_answer = st.chat_input("Enter candidate response...")
            if user_answer:
                st.session_state.messages.append({"role": "user", "content": user_answer})
                
                # 1. Run Evaluator Agent for this answer
                with st.spinner("Agent 2 (Evaluator) analyzing candidate response..."):
                    eval_res = run_evaluator_agent(
                        target_role=target_role,
                        question=st.session_state.latest_question,
                        answer=user_answer,
                        api_key=api_key,
                        model_name=model_name
                    )
                    st.session_state.latest_evaluation = eval_res

                # 2. Run Decision Agent for this evaluation
                with st.spinner("Agent 3 (Decision) evaluating difficulty & routing..."):
                    dec_res = run_decision_agent(
                        current_round=st.session_state.current_question_index + 1,
                        max_rounds=st.session_state.max_questions,
                        current_difficulty=st.session_state.current_difficulty,
                        evaluation=eval_res,
                        api_key=api_key,
                        model_name=model_name
                    )
                    st.session_state.latest_decision = dec_res

                # Record completed round into history
                completed_round = {
                    "round": st.session_state.current_question_index + 1,
                    "question": st.session_state.latest_question,
                    "reason": st.session_state.latest_question_reason,
                    "answer": user_answer,
                    "difficulty": st.session_state.current_difficulty,
                    "evaluation": eval_res,
                    "decision": dec_res
                }
                st.session_state.question_history.append(completed_round)
                st.session_state.current_question_index += 1
                st.session_state.current_difficulty = dec_res.get("target_difficulty", st.session_state.current_difficulty)

                # Check if interview complete
                if st.session_state.current_question_index >= st.session_state.max_questions:
                    st.session_state.interview_complete = True
                    with st.spinner("Agent 4 (Coach) compiling Executive Assessment Report..."):
                        report = run_coach_agent(
                            target_role=target_role,
                            interview_type=interview_type,
                            resume_snippet=resume_snippet,
                            question_history=st.session_state.question_history,
                            api_key=api_key,
                            model_name=model_name
                        )
                        st.session_state.coaching_report = report
                    st.rerun()
                else:
                    # 3. Run Interviewer Agent for next question
                    with st.spinner("Agent 1 (Interviewer) formulating next prompt..."):
                        next_q_res = run_interviewer_agent(
                            target_role=target_role,
                            resume_snippet=resume_snippet,
                            interview_type=interview_type,
                            current_difficulty=st.session_state.current_difficulty,
                            decision_action=dec_res.get("action", "move_next_topic"),
                            question_history=st.session_state.question_history,
                            api_key=api_key,
                            model_name=model_name
                        )
                        st.session_state.latest_question = next_q_res["question"]
                        st.session_state.latest_question_reason = next_q_res["reason"]
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"**Question {st.session_state.current_question_index + 1} ({st.session_state.current_difficulty} Difficulty):**\n\n{next_q_res['question']}"
                        })
                    st.rerun()

    # Multi-Agent Diagnostic Inspection Panel
    with diag_col:
        st.subheader("Multi-Agent Diagnostic Inspector")
        
        history = st.session_state.question_history
        if history:
            round_labels = [f"Round {item['round']} (Latest)" if idx == 0 else f"Round {item['round']}" for idx, item in enumerate(reversed(history))]
            round_map = {label: item for label, item in zip(round_labels, reversed(history))}
            
            selected_label = st.selectbox(
                "Inspect Round Diagnostics:",
                options=round_labels,
                index=0,
                key=f"inspector_select_{len(history)}",
                help="Automatically shows the newest answer evaluation. Click to view prior rounds."
            )
            selected_data = round_map[selected_label]
            
            selected_eval = selected_data.get("evaluation", {})
            selected_dec = selected_data.get("decision", {})
            selected_reason = selected_data.get("reason", "")
            selected_diff = selected_data.get("difficulty", "Medium")
        else:
            selected_eval = st.session_state.latest_evaluation
            selected_dec = st.session_state.latest_decision
            selected_reason = st.session_state.latest_question_reason
            selected_diff = st.session_state.current_difficulty

        with st.expander("Agent 1 — Interviewer Directive", expanded=True):
            if selected_reason:
                st.markdown(f"**Question Rationale:** {selected_reason}")
                st.markdown(f"**Target Difficulty:** `<span class='status-pill'>{selected_diff}</span>`", unsafe_allow_html=True)
            else:
                st.caption("Awaiting initial prompt generation...")

        with st.expander("Agent 2 — Evaluator Scorecard (JSON)", expanded=True):
            if selected_eval:
                metrics = [
                    ("Technical Accuracy", selected_eval.get("technical", 0)),
                    ("Communication", selected_eval.get("communication", 0)),
                    ("Confidence", selected_eval.get("confidence", 0)),
                    ("Clarity", selected_eval.get("clarity", 0)),
                    ("Technical Depth", selected_eval.get("depth", 0)),
                ]
                
                for label, score in metrics:
                    pct = score * 10
                    st.markdown(f"""
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #cbd5e1;">
                            <span>{label}</span>
                            <span><b>{score}/10</b></span>
                        </div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width: {pct}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if selected_eval.get("weakness"):
                    st.markdown(f"**Identified Area for Improvement:**\n> {selected_eval.get('weakness')}")
            else:
                st.caption("Awaiting candidate input for evaluation...")

        with st.expander("Agent 3 — Decision & Routing Logic", expanded=True):
            if selected_dec:
                action = selected_dec.get("action", "move_next_topic")
                reason = selected_dec.get("reasoning", "")
                
                st.markdown(f"**Orchestration Directive:** `{action}`")
                st.markdown(f"**Decision Reasoning:** {reason}")
                st.markdown(f"**Next Round Target Difficulty:** {selected_dec.get('target_difficulty')}")
            else:
                st.caption("Awaiting evaluator output for routing decision...")

    # Executive Assessment Report
    if st.session_state.interview_complete:
        st.divider()
        st.subheader("Executive Candidate Evaluation Report")
        
        st.markdown(st.session_state.coaching_report)
        
        st.download_button(
            label="Download Candidate Assessment Report (.md)",
            data=st.session_state.coaching_report,
            file_name=f"Candidate_Evaluation_{target_role.replace(' ', '_')}.md",
            mime="text/markdown"
        )
