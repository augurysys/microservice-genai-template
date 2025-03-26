# microservice-genai-template

# 🗂️ Project Structure

### 📁 `agents/`
> Agent and chain definitions  
Each agent can be modular (with prompt templates, tools, and LangGraph/LangChain logic). Useful for multi-agent systems.

### 📄 `workflow.py`  
> Workflow orchestration

### 📄 `state.py`  
> Shared state definitions

### 📁 `example_agent1/`
> Specific agent type  
- 📁 `prompts/` – Prompt templates  
- 📄 `agent.py` – Agent logic (e.g., workflow, automation, RAG)

---

### 📁 `core/`
> 🔧 LLM core logic  
- LLM instantiation  
- Evaluation utils  
- LangSmith integration

### 📁 `api/`
> 🚀 FastAPI routers & endpoints

### 📁 `models/`
> 🧱 Pydantic schemas for request/response bodies

### 📁 `tests/`
> 🧪 Tests for agents, prompts, API

### 📁 `ingestion/`
> 📥 Data ingestion + embedding creation

### 📁 `tools/`
> 🛠️ Reusable tools for agents

### 📁 `memory/`
> 🧠 Short-term & long-term memory modules

---

### 📁 `evaluations/`
> 📊 Evaluation methods  
- 📁 `llm_as_a_judge/` – Use LLMs for eval  
- 📁 `dataset_eval/` – Dataset-driven eval

### 📁 `utils/`
> ⚙️ Utility functions

### 📁 `async/`
> 🔄 Async event entry point

### 📁 `repository/`
> 🗃️ DB layer (persistence logic)

### 📁 `logic/`
> 🧩 *(Optional)* Domain/business logic layer
