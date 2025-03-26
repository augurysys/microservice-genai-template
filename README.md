# 🗂️ Project Structure

### 📁 `agents/`
> Agent and chain definitions  
Each agent can be modular (with prompt templates, tools, and LangGraph/LangChain logic). Useful for multi-agent systems.

- 📄 `workflow.py` – Workflow orchestration
- 📄 `state.py` – Shared state definitions
- 📁 `example_agent1/` – Specific agent type
  - 📁 `prompts/` – Prompt templates
  - 📄 `agent.py` – Agent logic (e.g., workflow, automation, RAG)

---

### 📁 `core/`
> 🔧 LLM core logic  
- LLM instantiation  
- Generic evaluation logic  
- LangSmith tracing integration

### 📁 `api/`
> 🚀 FastAPI routers & endpoints

### 📁 `models/`
> 🧱 Pydantic schemas for request/response bodies

### 📁 `tests/`
> 🧪 Unit & integration tests  
- Agents  
- Prompts  
- API endpoints

### 📁 `ingestion/`
> 📥 Data ingestion & embedding creation

### 📁 `tools/`
> 🛠️ Reusable tools across agents

### 📁 `memory/`
> 🧠 Agent memory modules  
- Short-term memory  
- Long-term memory

---

### 📁 `evaluations/`
> 📊 Evaluation implementations

- 📁 `llm_as_a_judge/` – Evaluation via LLM feedback
- 📁 `dataset_eval/` – Dataset-based performance eval

### 📁 `utils/`
> ⚙️ General utility functions

### 📁 `async/`
> 🔄 Async event entry point

### 📁 `repository/`
> 🗃️ Database access and persistence layer

### 📁 `logic/`
> 🧩 *(Optional)* Domain/business logic (if a service layer is needed)
