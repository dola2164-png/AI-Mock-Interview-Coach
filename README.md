# Enterprise Multi-Agent AI Interview & Coaching Platform 💼

An adaptive, multi-agent AI candidate assessment and coaching system built with **LangGraph**, **Streamlit**, and **Groq (Llama 3.3 70B)**. Designed to conduct realistic, role-tailored mock interviews and deliver executive competency reports.

---

## 🌟 Architecture & Multi-Agent Design

The platform coordinates **4 specialized AI agents** using a stateful **LangGraph** `StateGraph` flow:

```
                                  +-----------------------+
                                  |     Candidate UI      |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   Interviewer Agent   |<------+
                                  +-----------+-----------+       |
                                              |                   |
                                              v                   |
                                  +-----------------------+       | (Rounds 1 to 5-7)
                                  |    Evaluator Agent    |       |
                                  +-----------+-----------+       |
                                              |                   |
                                              v                   |
                                  +-----------------------+       |
                                  |    Decision Agent     +-------+
                                  +-----------+-----------+
                                              | (After max rounds)
                                              v
                                  +-----------------------+
                                  |      Coach Agent      |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Executive Report (.md)|
                                  +-----------------------+
```

### Agent Roles & Responsibilities

1. **Agent 1 — Interviewer (`agents/interviewer.py`)**
   - **Persona**: Professional, empathetic, senior technical interviewer.
   - **Function**: Formulates tailored interview questions based on target role, resume snippet, session focus (Technical / Behavioral / Case Study / Mixed), and target difficulty. Follows action directives (`probe_deeper`, `move_next_topic`) passed from the Decision Agent.

2. **Agent 2 — Evaluator (`agents/evaluator.py`)**
   - **Persona**: Strict, objective candidate evaluator.
   - **Function**: Evaluates responses across 5 core dimensions on a 1–10 scale:
     - `technical`: Concept correctness & domain accuracy
     - `communication`: Professional phrasing & structure
     - `confidence`: Tone assertiveness & lack of hedging
     - `clarity`: Directness and conciseness
     - `depth`: Technical granularity & STAR method detail
   - **Output**: Validated Pydantic JSON structure containing scores, identified weakness, and `follow_up_needed` boolean flag.

3. **Agent 3 — Decision Agent (`agents/decision.py`)**
   - **Persona**: Adaptive interview controller.
   - **Function**: Analyzes evaluator JSON output and dictates the next step:
     - `probe_deeper`: Triggers when technical depth is low (<6/10) or `follow_up_needed` is true.
     - `increase_difficulty`: Scales difficulty from Medium to Hard when candidate scores >= 8.0 across metrics.
     - `decrease_difficulty`: Lowers difficulty to Easy when technical scores drop < 5.0.
     - `move_next_topic`: Default progression when performance is satisfactory.

4. **Agent 4 — Coach Agent (`agents/coach.py`)**
   - **Persona**: Executive career coach & lead technical reviewer.
   - **Function**: Synthesizes the complete transcript and evaluator scorecards into an **Executive Assessment Report** (Markdown format) featuring overall score, core strengths, technical gaps, communication tips, and a 7-Day custom practice plan.

---

## 📁 Repository Structure

```
ai-interview-coach/
├── agents/
│   ├── __init__.py
│   ├── interviewer.py    # Agent 1 logic
│   ├── evaluator.py      # Agent 2 logic
│   ├── decision.py       # Agent 3 logic
│   └── coach.py          # Agent 4 logic
├── graph/
│   ├── __init__.py
│   ├── state.py          # TypedDict InterviewState definition
│   └── workflow.py       # StateGraph orchestration & conditional routing
├── prompts/
│   ├── interviewer.txt   # External prompt template for Agent 1
│   ├── evaluator.txt     # External prompt template for Agent 2
│   ├── decision.txt      # External prompt template for Agent 3
│   └── coach.txt         # External prompt template for Agent 4
├── .streamlit/
│   └── config.toml       # Streamlit client configuration
├── app.py                # Streamlit UI & Interactive Multi-Agent Inspector
├── config.py             # LLM setup & Groq API key manager
├── requirements.txt      # Project dependencies
└── README.md             # Technical documentation & transcripts
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- A free **Groq API Key** from [console.groq.com](https://console.groq.com)

### 2. Environment Setup

```bash
# Navigate to project root
cd ai-interview-coach

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Key Configuration

Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_free_groq_api_key_here
```
*(Key is loaded privately from `.env` and never displayed on the UI).*

### 4. Launch Application

```bash
streamlit run app.py
```
Open browser at `http://localhost:8501`.

---

## 💡 Key Design Decisions & Trade-offs

1. **LangGraph vs Linear Chain**:
   - *Decision*: Used LangGraph `StateGraph` for explicit node routing and state persistence.
   - *Trade-off*: Slightly higher graph setup complexity vs a linear chain, but allows true conditional branching (`probe_deeper`, difficulty scaling) based on evaluator metrics.

2. **Groq (Llama 3.3 70B) LLM Engine**:
   - *Decision*: Adopted Groq for ultra-fast, 100% free LLM inference with zero latency bottlenecks during multi-agent turns.

3. **Externalized Prompts (`prompts/`)**:
   - *Decision*: Separated all system prompts into raw `.txt` files in `prompts/`.
   - *Trade-off*: Eliminates code bloat and enables prompt iteration without touching python code.

4. **Dynamic Scoring vs Anchor Bias Prevention**:
   - *Decision*: Removed fixed numerical examples in `prompts/evaluator.txt` and enforced explicit dynamic grading rules based on exact answer quality.

---

## 📝 Example Interview Transcripts

### Transcript 1: Strong Candidate (Frontend Engineer Intern)
**Role**: Frontend Engineer Intern | **Focus**: Mixed | **Rounds**: 3

```markdown
### Round 1 (Medium Difficulty)
Interviewer Question: "Can you explain the concept of progressive enhancement in web development and how you would implement it?"
Candidate Answer: "Progressive enhancement is a design strategy where we build a basic working core HTML/CSS structure first for all devices/browsers, and then add advanced JavaScript capabilities like client-side validation, SPA routing, and dynamic search suggestions for modern browsers."

Evaluator Scorecard:
- Technical: 9/10 | Communication: 9/10 | Confidence: 8/10 | Clarity: 9/10 | Depth: 8/10
- Weakness: "Could have mentioned specific fallback strategies or aria-live accessibility attributes for screen readers."
- Follow-up Needed: False

Decision Agent Directive: `increase_difficulty`
- Reasoning: Candidate demonstrated exceptional clarity and architectural understanding. Scaling difficulty to Hard.

---

### Round 2 (Hard Difficulty)
Interviewer Question: "How would you handle state management and performance optimization in a large React app with high-frequency WebSocket updates?"
Candidate Answer: "I would decouple high-frequency WebSocket state from the main React component render tree using a dedicated store like Zustand or RxJS. To prevent UI jank, I would batch updates using requestAnimationFrame or React 18 useDeferredValue, and memoize heavy sub-trees with React.memo."

Evaluator Scorecard:
- Technical: 9/10 | Communication: 9/10 | Confidence: 9/10 | Clarity: 9/10 | Depth: 9/10
- Weakness: "None noted; candidate covered rendering pipeline, batching, and decoupling cleanly."
- Follow-up Needed: False

Decision Agent Directive: `move_next_topic`
- Reasoning: Exceptional response under Hard difficulty. Moving to system design trade-offs.

---

Executive Report Summary:
- Overall Score: 92/100
- Category: Outstanding (Ready for Placement)
```

---

### Transcript 2: Weak Candidate (Data Analyst Intern)
**Role**: Data Analyst Intern | **Focus**: Technical | **Rounds**: 2

```markdown
### Round 1 (Medium Difficulty)
Interviewer Question: "How do you handle missing values in a SQL dataset before running an aggregation query?"
Candidate Answer: "I just delete the rows with nulls or use AVG()."

Evaluator Scorecard:
- Technical: 4/10 | Communication: 5/10 | Confidence: 5/10 | Clarity: 6/10 | Depth: 3/10
- Weakness: "Candidate fails to explain NULL handling functions (COALESCE, NULLIF), imputation strategies, or the difference between row deletion vs aggregate distortion."
- Follow-up Needed: True

Decision Agent Directive: `probe_deeper`
- Reasoning: Technical depth score is below 6. Probing deeper into SQL NULL handling syntax without scaling difficulty.

---

### Round 2 (Medium Difficulty - Probe Deeper)
Interviewer Question: "Can you provide the specific SQL function you would use to replace NULL values with a default value of 0 in a SELECT query?"
Candidate Answer: "Maybe IF NULL or something? I am not sure of the exact function name."

Evaluator Scorecard:
- Technical: 4/10 | Communication: 4/10 | Confidence: 3/10 | Clarity: 5/10 | Depth: 2/10
- Weakness: "Candidate lacks basic familiarity with standard SQL COALESCE or IFNULL functions."
- Follow-up Needed: False

Decision Agent Directive: `decrease_difficulty`
- Reasoning: Technical score < 5. Decreasing target difficulty to Easy for foundational concepts.

---

Executive Report Summary:
- Overall Score: 45/100
- Category: Needs Foundational Revision in SQL & Data Imputation
```

---

### Transcript 3: Tricky / Edge Case Candidate (Product Manager Intern)
**Role**: Product Manager Intern | **Focus**: Case Study | **Rounds**: 2

```markdown
### Round 1 (Medium Difficulty)
Interviewer Question: "How would you measure the success of launching a new feature like Instagram Stories for a professional network platform?"
Candidate Answer: "I don't know much about metrics, maybe I'd just ask users if they like it or check if downloads go up."

Evaluator Scorecard:
- Technical: 3/10 | Communication: 4/10 | Confidence: 3/10 | Clarity: 5/10 | Depth: 2/10
- Weakness: "Candidate gave an off-topic / evasive 'I don't know' reply without structuring a product metrics framework (DAU, Retention, Adoption Rate)."
- Follow-up Needed: True

Decision Agent Directive: `probe_deeper`
- Reasoning: Candidate replied with uncertainty. Providing a simplified framework prompt to test problem-solving resilience.

---

### Round 2 (Medium Difficulty - Structured Recovery)
Interviewer Question: "Let's break it down step by step. What is one key user engagement action you would track daily to see if people are using the new feature?"
Candidate Answer: "Oh! Daily Active Users who post at least one story per day, and the retention rate of users who return within 7 days."

Evaluator Scorecard:
- Technical: 8/10 | Communication: 7/10 | Confidence: 7/10 | Clarity: 8/10 | Depth: 7/10
- Weakness: "Good recovery on primary metrics, though didn't mention guardrail metrics like feed cannibalization."
- Follow-up Needed: False

Decision Agent Directive: `move_next_topic`
- Reasoning: Candidate successfully recovered when prompted with a structured sub-question.

---

Executive Report Summary:
- Overall Score: 68/100
- Category: Moderate Potential (Requires Guidance on Initial Framework Structure)
```
