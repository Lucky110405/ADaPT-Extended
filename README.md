# ADaPT-Extended: LLM-Based Autonomous Agent for Task Decomposition

An extended implementation based on the paper **"ADaPT: As-Needed Decomposition and Planning with Language Models"** (NAACL 2024 Findings), with a multi-agent orchestration workflow featuring persistent memory and atomic skill caching.

## Architecture Overview

```
Task Input
    └─> Orchestration Agent (LLM)
            └─> Agent 1: Task Type & Confidence Classifier
                    ├─> [Simple / High Confidence] → Direct Execution → Return
                    └─> [Complex] → External Help Req. Check Agent
                                        ├─> [Needs Clarification] → Cross Questioning Agent LLM
                                        └─> [Has Context] → Planner & Decomposition Agent
                                                                └─> subtask 1, subtask 2, ... subtask N
                                                                        └─> Persistent Memory (stores plan)
                                                                                └─> Database (Atomic Skills Cache)
```

## Key Components

| Component | Description |
|-----------|-------------|
| `OrchestratorAgent` | Entry point; routes tasks to appropriate agents |
| `TaskClassifierAgent` | Classifies task complexity & confidence score |
| `ExternalHelpAgent` | Checks if tools/clarification are needed |
| `CrossQuestioningAgent` | Asks clarifying questions to resolve ambiguity |
| `PlannerDecompositionAgent` | Decomposes complex tasks into subtasks (AND/OR/NEXT/IF-THEN) |
| `ExecutorAgent` | Executes individual subtasks |
| `PersistentMemory` | Program-counter-like store of execution state |
| `SkillDatabase` | Caches successful decomposition plans as reusable atomic skills |

## Installation

```bash
pip install -r requirements.txt
```

Add your OpenAI/Anthropic API key to a `.env` file:
```
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Start

```bash
# Run a single task
python main.py --task "Organize a conference for 200 attendees"

# Run with custom depth
python main.py --task "Plan a product launch" --max_depth 3

# Run experiments on benchmark tasks
python experiments/run_benchmark.py

# Launch web UI
python app.py
```

## Project Structure

```
adapt_agent/
├── agents/
│   ├── orchestrator.py          # Main orchestration agent
│   ├── task_classifier.py       # Task type & confidence classifier
│   ├── external_help_agent.py   # Checks tool/context needs
│   ├── cross_questioning.py     # Clarification agent
│   ├── planner.py               # Decomposition & planning agent
│   └── executor.py              # Subtask executor
├── memory/
│   ├── persistent_memory.py     # Program-counter-like execution state
│   └── skill_database.py        # Atomic skill cache (SQLite)
├── tools/
│   ├── tool_registry.py         # Tool registration & dispatch
│   ├── web_search.py            # Web search tool
│   └── calculator.py            # Calculator tool
├── prompts/
│   ├── classifier_prompts.py
│   ├── planner_prompts.py
│   ├── executor_prompts.py
│   └── cross_question_prompts.py
├── config/
│   └── settings.py              # Global config
├── experiments/
│   └── run_benchmark.py         # Benchmark runner
├── utils/
│   ├── llm_client.py            # Unified LLM API client
│   └── logger.py                # Structured logging
├── data/
│   ├── tasks/                   # Sample benchmark tasks
│   └── results/                 # Experiment results
├── main.py                      # CLI entry point
├── app.py                       # Streamlit web UI
└── requirements.txt
```

## Novel Contributions vs ADaPT (Base Paper)

1. **Multi-agent orchestration**: Dedicated agents for classification, clarification, and planning
2. **Persistent memory**: PC-like program counter that stores execution state, enabling resume and rollback
3. **Atomic Skill Caching**: Successful complex plans are saved to a DB and retrieved for similar tasks
4. **Cross-questioning**: Ambiguous tasks trigger a clarification loop before planning
5. **Reasoning depth comparison**: Built-in benchmarking of agent vs single-prompt LLM

## Citation

```bibtex
@inproceedings{prasad-etal-2024-adapt,
    title = "{AD}a{PT}: As-Needed Decomposition and Planning with Language Models",
    author = "Prasad, Archiki et al.",
    booktitle = "Findings of the Association for Computational Linguistics: NAACL 2024",
    year = "2024",
}
```

## Run the Streamlit UI

You can launch the project's web UI with Streamlit. This provides an interactive interface for entering tasks and viewing decomposition traces.

1. Install dependencies (recommended inside a virtual environment):

```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

If the app imports your agent modules which call external LLM services, network requests may block the UI; ensure your LLM client is configured (see `.env`) or run the app in an environment with the required credentials.

