---
name: adk-skill
description: Use this skill whenever the user wants to build agentic AI chatbot applications using Google Agent Development Kit (ADK). It covers single agents, multi-agent systems, tool definitions, agent delegation, session state management, callbacks/guardrails, workflow orchestration (sequential, parallel, loop), and deployment. Make sure to use this skill whenever the user mentions ADK, Agent Development Kit, agentic chatbot, multi-agent system, agent orchestration, agent delegation, agent team, agent pipeline, or wants to build any kind of AI agent that goes beyond simple API calls — even if they don't explicitly say "ADK".
---

# Google ADK Python Skill

This skill provides comprehensive reference documentation and best practices for building agentic AI chatbot applications using the Google Agent Development Kit (ADK) with Python.
All reference material is included inline below — no external reference files are needed.

## When to Use ADK vs Plain Gemini API

- **Use this skill (ADK)** when the user needs: multi-agent systems, tool-using agents, stateful conversations, agent delegation/routing, guardrails/callbacks, workflow orchestration, or any agentic architecture.
- **Use `google-gemini-python` skill instead** when the user only needs: direct text generation, JSON extraction, image/document processing via the Gemini API without agent orchestration.

ADK builds on top of the Gemini API — it provides the agentic framework layer (agents, tools, sessions, runners) while Gemini provides the underlying LLM.

## Key Concepts

1. **Agent Types**: `Agent`/`LlmAgent` (LLM-powered), `SequentialAgent`/`ParallelAgent`/`LoopAgent` (workflow), `BaseAgent` (custom)
2. **Tools**: Python functions with type hints and docstrings become callable tools automatically
3. **Multi-Agent Hierarchy**: Parent agents delegate to sub-agents via LLM-driven transfer or `AgentTool`
4. **Session & State**: `InMemorySessionService` for dev, persistent services for production; `output_key` passes data between agents
5. **Callbacks**: `before_model_callback`, `before_tool_callback`, etc. for guardrails and control
6. **Runner**: `Runner` orchestrates agent execution with `run_async` event loop

## Common Workflows Covered

- Single Agent with Tools
- Multi-Agent Chatbot with Delegation (Coordinator/Dispatcher)
- Sequential Pipeline (step-by-step processing)
- Parallel Fan-Out/Gather (concurrent tasks)
- Iterative Refinement Loop (progressive improvement)
- Generator-Critic Review Pattern
- Stateful Agent with Session State
- Input/Output Guardrails via Callbacks
- Structured JSON Output with Pydantic schemas
- Deployment to Vertex AI Agent Engine, Cloud Run, GKE

## Environment Setup

A `.env.sample` file must be included in every ADK project. After development, the user copies it to `.env` and fills in the values:

```
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

You MUST always generate a `.env.sample` file with these variables in every ADK project you create. After development is complete, remind the user to create and fill the `.env` file.

## Supported Models

ONLY use Google Gemini models:
- `gemini-2.5-flash` — Fast, cost-effective (default choice)
- `gemini-2.5-pro` — More powerful, for complex reasoning

Do NOT use LiteLLM, OpenAI, Anthropic, Ollama, or any other non-Gemini model.

## Installation Quick Reference

```bash
pip install google-adk                                          # Core ADK
pip install google-cloud-aiplatform[adk,agent_engines]          # Vertex AI deployment
pip install python-dotenv google-auth                           # Env and auth
```

## Minimal Agent Pattern

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="my_chatbot",
    model="gemini-2.5-flash",
    instruction="You are a helpful chatbot assistant.",
    description="A general-purpose chatbot.",
    tools=[my_tool_function]
)
```

## Project Structure

```
my_agent/
├── __init__.py          # from . import agent
├── agent.py             # Defines root_agent
├── .env.sample          # Environment variable template (ALWAYS include this)
├── .env                 # Actual env values (user fills after dev, gitignored)
└── requirements.txt
```

Run with: `adk web my_agent` (dev UI) or `adk run my_agent` (CLI)

---

# Complete Google ADK Python Reference

This documentation is distilled from the official ADK repository (`google/adk-python`) and covers everything needed to build agentic AI chatbot applications using the Google Agent Development Kit.

It assumes the following are already present:

* Python 3.10+ installed
* A valid Google Cloud project with Vertex AI enabled
* A service account JSON key file for authentication
* A `.env` file (created from `.env.sample`) with the following variables:
  * `GOOGLE_CLOUD_PROJECT` — Your GCP project ID
  * `GOOGLE_CLOUD_LOCATION` — Vertex AI region (e.g., `us-central1`)
  * `GOOGLE_APPLICATION_CREDENTIALS` — Path to service account JSON key
  * `GOOGLE_GENAI_USE_VERTEXAI=TRUE`

**Important**: Always generate a `.env.sample` file in every ADK project with these variables. After development, ask the user to create a `.env` file and fill in the values.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation & Setup](#2-installation--setup)
3. [Project Structure](#3-project-structure)
4. [Agent Types](#4-agent-types)
5. [Defining an LLM Agent](#5-defining-an-llm-agent)
6. [Tools](#6-tools)
7. [Multi-Agent Systems](#7-multi-agent-systems)
8. [Workflow Agents](#8-workflow-agents)
9. [Session, State & Memory](#9-session-state--memory)
10. [Runner & Execution](#10-runner--execution)
11. [Callbacks & Guardrails](#11-callbacks--guardrails)
12. [Model Configuration](#12-model-configuration)
13. [Structured Output](#13-structured-output)
14. [Dev UI & Evaluation](#14-dev-ui--evaluation)
15. [Deployment](#15-deployment)
16. [Complete Examples](#16-complete-examples)

---

## 1. Overview

The Agent Development Kit (ADK) is an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents, optimized for Gemini and the Google ecosystem.

Key features:
- **Code-First Development**: Define agent logic, tools, and orchestration directly in Python
- **Rich Tool Ecosystem**: Pre-built tools, custom functions, OpenAPI specs, LangChain/CrewAI integrations
- **Modular Multi-Agent Systems**: Compose multiple specialized agents into flexible hierarchies
- **Deploy Anywhere**: Cloud Run, Vertex AI Agent Engine, GKE, or self-hosted

---

## 2. Installation & Setup

### Install ADK

```bash
pip install google-adk
```

For Vertex AI deployment support:

```bash
pip install google-cloud-aiplatform[adk,agent_engines]
```

For environment variable loading and authentication:

```bash
pip install python-dotenv google-auth
```

### Environment Configuration

Every ADK project MUST include a `.env.sample` file:

```
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

The user copies this to `.env` and fills in the values. Load it in your agent code:

```python
from dotenv import load_dotenv
load_dotenv()
```

For Vertex AI authentication via ADC (alternative to service account key):

```bash
gcloud auth application-default login
```

---

## 3. Project Structure

A standard ADK agent project follows this layout:

```
my_agent/
├── __init__.py          # Must contain: from . import agent
├── agent.py             # Agent definition with root_agent variable
├── .env.sample          # Environment variable template (ALWAYS include this)
├── .env                 # Actual env values (user fills after dev, gitignored)
└── requirements.txt     # Dependencies
```

The `__init__.py` file must import the agent module:

```python
from . import agent
```

The `agent.py` must expose a `root_agent` variable:

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="A helpful assistant agent.",
    tools=[]
)
```

---

## 4. Agent Types

ADK provides three core agent categories:

| Type | Engine | Determinism | Best For |
|:-----|:-------|:------------|:---------|
| **LLM Agent** (`LlmAgent` / `Agent`) | Large Language Model | Non-deterministic | Reasoning, generation, tool use, dynamic decisions |
| **Workflow Agent** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) | Predefined logic | Deterministic | Structured processes, orchestration |
| **Custom Agent** (`BaseAgent` subclass) | Custom code | Either | Unique logic, specific integrations |

### LLM Agent

The primary agent type, powered by an LLM for reasoning, understanding, and tool use.

```python
from google.adk.agents import Agent  # Agent is an alias for LlmAgent

agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="Handles general questions.",
    tools=[my_tool_function]
)
```

### Workflow Agents

Control execution flow of sub-agents without using an LLM for orchestration:

- **`SequentialAgent`**: Runs sub-agents one after another
- **`ParallelAgent`**: Runs sub-agents concurrently
- **`LoopAgent`**: Repeats sub-agents until a condition is met or max iterations reached

### Custom Agents

Extend `BaseAgent` directly for fully custom orchestration:

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class MyCustomAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Custom logic here
        yield Event(author=self.name, content=...)
```

---

## 5. Defining an LLM Agent

### Core Parameters

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    # Required
    name="customer_support_agent",           # Unique identifier
    model="gemini-2.5-flash",               # LLM model to use

    # Recommended
    instruction="You are a helpful customer support agent...",  # Behavior guide
    description="Handles customer support inquiries.",          # Used by other agents for routing

    # Optional
    tools=[get_order_status, refund_tool],   # Available tools
    sub_agents=[billing_agent, tech_agent],  # Child agents for delegation
    output_key="support_result",             # Save response to session state
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=500
    ),
    include_contents='default',              # 'default' or 'none' for stateless
)
```

### Instructions Best Practices

- Be clear and specific
- Use Markdown for complex instructions
- Provide examples (few-shot)
- Guide tool use explicitly — explain *when* and *why*
- Use `{var}` syntax for dynamic state injection: `"Welcome {user_name}"`
- Use `{artifact.var}` for artifact content injection
- Append `?` to ignore missing values: `{optional_var?}`

### Global Instructions

For instructions that apply to ALL agents in a system, use `global_instruction` on the root agent:

```python
root_agent = Agent(
    name="root",
    model="gemini-2.5-flash",
    global_instruction="Always be polite and professional.",
    instruction="You coordinate tasks between sub-agents.",
    sub_agents=[agent_a, agent_b]
)
```

---

## 6. Tools

Tools give agents capabilities beyond the LLM's built-in knowledge. The LLM uses function names, docstrings, and parameter schemas to decide which tool to call.

### Custom Function Tools

The simplest way to create a tool — write a Python function with type hints and a docstring:

```python
def get_weather(city: str) -> dict:
    """Retrieves the current weather for a specified city.

    Args:
        city: The name of the city.

    Returns:
        dict with status and weather report.
    """
    if city.lower() == "new york":
        return {"status": "success", "report": "Sunny, 25°C"}
    return {"status": "error", "error_message": f"No data for '{city}'."}

agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    instruction="Use get_weather to answer weather questions.",
    tools=[get_weather]  # Pass function directly
)
```

### Built-in Tools

ADK provides pre-built tools:

```python
from google.adk.tools import google_search, load_memory

agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="Search the web to answer questions.",
    tools=[google_search]
)
```

### AgentTool — Agent as a Tool

Wrap another agent as a callable tool:

```python
from google.adk.tools import agent_tool

specialist = Agent(name="Specialist", model="gemini-2.5-flash", ...)
specialist_tool = agent_tool.AgentTool(agent=specialist)

coordinator = Agent(
    name="Coordinator",
    model="gemini-2.5-flash",
    instruction="Use the Specialist tool for complex tasks.",
    tools=[specialist_tool]
)
```

### FunctionTool Wrapper

For explicit wrapping:

```python
from google.adk.tools import FunctionTool

my_tool = FunctionTool(func=my_function)
```

### OpenAPI Tools

Generate tools from an OpenAPI spec:

```python
from google.adk.tools.openapi_tool.openapi_spec_parser import OpenApiToolset

toolset = OpenApiToolset(spec_str=my_openapi_spec_string)
# Or from dict: toolset = OpenApiToolset(spec_dict=my_openapi_spec_dict)

agent = Agent(
    name="api_agent",
    model="gemini-2.5-flash",
    tools=toolset.get_tools()
)
```

### LangChain Tool Integration

```python
from google.adk.tools.langchain_tool import LangchainTool

# Wrap a LangChain tool
adk_tool = LangchainTool(tool=langchain_tool_instance)
agent = Agent(name="agent", model="gemini-2.5-flash", tools=[adk_tool])
```

### CrewAI Tool Integration

```python
from google.adk.tools.crewai_tool import CrewaiTool

adk_tool = CrewaiTool(tool=crewai_tool_instance)
agent = Agent(name="agent", model="gemini-2.5-flash", tools=[adk_tool])
```

---

## 7. Multi-Agent Systems

ADK supports composing multiple agents into hierarchical systems for complex applications.

### Agent Hierarchy

```python
from google.adk.agents import LlmAgent

greeter = LlmAgent(name="Greeter", model="gemini-2.5-flash", description="Handles greetings.")
task_doer = LlmAgent(name="TaskExecutor", model="gemini-2.5-flash", description="Executes tasks.")

coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.5-flash",
    instruction="Route greetings to Greeter and tasks to TaskExecutor.",
    description="Main coordinator.",
    sub_agents=[greeter, task_doer]
)
```

### LLM-Driven Delegation (Agent Transfer)

When sub-agents are present, ADK's `AutoFlow` enables the LLM to dynamically route tasks via `transfer_to_agent`:

```python
# The LLM generates: transfer_to_agent(agent_name='Greeter')
# ADK framework handles the routing automatically
```

Requirements:
- Parent agent needs clear `instruction` on when to transfer
- Sub-agents need distinct `description` fields
- Transfer scope (parent, sub-agent, siblings) can be configured

### Common Multi-Agent Patterns

**1. Coordinator/Dispatcher**: Central agent routes requests to specialists

```python
billing = LlmAgent(name="Billing", description="Handles billing inquiries.")
support = LlmAgent(name="Support", description="Handles technical support.")

coordinator = LlmAgent(
    name="HelpDesk",
    model="gemini-2.5-flash",
    instruction="Route billing issues to Billing, tech problems to Support.",
    sub_agents=[billing, support]
)
```

**2. Sequential Pipeline**: Output of one step feeds the next

```python
from google.adk.agents import SequentialAgent

validator = LlmAgent(name="Validate", output_key="validation_status", ...)
processor = LlmAgent(name="Process", instruction="Process if state 'validation_status' is valid.", ...)
reporter = LlmAgent(name="Report", instruction="Report the result.", ...)

pipeline = SequentialAgent(name="Pipeline", sub_agents=[validator, processor, reporter])
```

**3. Parallel Fan-Out/Gather**: Run tasks concurrently, then aggregate

```python
from google.adk.agents import ParallelAgent, SequentialAgent

fetch_weather = LlmAgent(name="Weather", output_key="weather", ...)
fetch_news = LlmAgent(name="News", output_key="news", ...)

gatherer = ParallelAgent(name="Gather", sub_agents=[fetch_weather, fetch_news])
synthesizer = LlmAgent(name="Synthesizer", instruction="Combine 'weather' and 'news' from state.", ...)

workflow = SequentialAgent(name="FetchAndSynthesize", sub_agents=[gatherer, synthesizer])
```

**4. Iterative Refinement (Loop)**: Progressively improve output

```python
from google.adk.agents import LoopAgent

refiner = LlmAgent(name="Refiner", output_key="draft", ...)
checker = LlmAgent(name="Checker", output_key="quality_status", ...)

# Custom agent to escalate when quality passes
class StopChecker(BaseAgent):
    async def _run_async_impl(self, ctx):
        status = ctx.session.state.get("quality_status", "fail")
        yield Event(author=self.name, actions=EventActions(escalate=(status == "pass")))

loop = LoopAgent(
    name="RefineLoop",
    max_iterations=5,
    sub_agents=[refiner, checker, StopChecker(name="Stop")]
)
```

**5. Generator-Critic (Review Pattern)**:

```python
generator = LlmAgent(name="Writer", output_key="draft_text", ...)
reviewer = LlmAgent(name="Reviewer", instruction="Review 'draft_text' for accuracy.", output_key="review_status", ...)

review_pipeline = SequentialAgent(name="WriteAndReview", sub_agents=[generator, reviewer])
```

---

## 8. Workflow Agents

### SequentialAgent

Executes sub-agents one after another in order. Each agent can access state set by previous agents.

```python
from google.adk.agents import SequentialAgent, LlmAgent

step1 = LlmAgent(name="Fetch", model="gemini-2.5-flash", output_key="data", ...)
step2 = LlmAgent(name="Process", model="gemini-2.5-flash",
                  instruction="Process data from state key 'data'.", ...)

pipeline = SequentialAgent(name="Pipeline", sub_agents=[step1, step2])
```

### ParallelAgent

Executes sub-agents concurrently. All share the same `session.state` — use distinct keys to avoid race conditions.

```python
from google.adk.agents import ParallelAgent

fetch_a = LlmAgent(name="FetchA", output_key="data_a", ...)
fetch_b = LlmAgent(name="FetchB", output_key="data_b", ...)

parallel = ParallelAgent(name="ParallelFetch", sub_agents=[fetch_a, fetch_b])
```

### LoopAgent

Repeats sub-agents sequentially until `max_iterations` is reached or a sub-agent yields an `Event` with `escalate=True`.

```python
from google.adk.agents import LoopAgent

process = LlmAgent(name="Process", ...)
checker = MyCheckAgent(name="Checker")  # Custom agent that escalates when done

loop = LoopAgent(name="Poller", max_iterations=10, sub_agents=[process, checker])
```

---

## 9. Session, State & Memory

### Session

A `Session` represents a single ongoing conversation. It contains:
- Chronological sequence of `Events` (messages and actions)
- Temporary data (`State`) for the current conversation

### State (`session.state`)

Data stored within a specific session. Used for passing information between agents and turns.

**Reading and writing state:**

```python
# In a tool or callback:
value = tool_context.state.get("my_key", "default")
tool_context.state["my_key"] = "new_value"

# Using output_key on an agent:
agent = LlmAgent(name="Agent", output_key="result", ...)
# After execution: session.state["result"] contains the agent's response
```

**State prefixes for persistence control:**

```python
from google.adk.sessions import State

# App-level (shared across all sessions of an app):
tool_context.state[State.APP_PREFIX + "global_config"] = config

# User-level (shared across sessions of a user):
tool_context.state[State.USER_PREFIX + "preference"] = "dark_mode"

# Temp-level (cleared between invocations):
tool_context.state[State.TEMP_PREFIX + "step_counter"] = 0
```

### SessionService Implementations

```python
# For development/testing (data lost on restart):
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()

# Create a session:
session = await session_service.create_session(
    app_name="my_app", user_id="user_1", session_id="session_1"
)

# With initial state:
session = await session_service.create_session(
    app_name="my_app", user_id="user_1", session_id="session_1",
    state={"preference": "celsius"}
)
```

For production, use persistent backends:
- `DatabaseSessionService` (SQL databases)
- `VertexAiSessionService` (Vertex AI Agent Engine)
- `FirestoreSessionService` (Google Firestore)

### Memory (Long-Term Knowledge)

Memory spans across sessions — a searchable archive the agent can consult.

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory

memory_service = InMemoryMemoryService()

# Agent with memory access:
agent = LlmAgent(
    model="gemini-2.5-flash",
    name="MemoryAgent",
    instruction="Use load_memory tool to recall past conversations.",
    tools=[load_memory]
)

# Runner with memory service:
runner = Runner(
    agent=agent,
    app_name="my_app",
    session_service=session_service,
    memory_service=memory_service
)
```

For production, use `VertexAiRagMemoryService` with a configured RAG Corpus.

---

## 10. Runner & Execution

The `Runner` orchestrates agent execution and manages the event loop.

### Basic Setup

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. Define agent
agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are helpful.",
    tools=[my_tool]
)

# 2. Session service
session_service = InMemorySessionService()

# 3. Create session
session = await session_service.create_session(
    app_name="my_app", user_id="user_1", session_id="session_1"
)

# 4. Create runner
runner = Runner(
    agent=agent,
    app_name="my_app",
    session_service=session_service
)

# 5. Send a message and get response
user_message = types.Content(
    role='user',
    parts=[types.Part(text="What's the weather in Tokyo?")]
)

async for event in runner.run_async(
    user_id="user_1",
    session_id="session_1",
    new_message=user_message
):
    if event.is_final_response() and event.content and event.content.parts:
        print(event.content.parts[0].text)
```

### Helper Pattern for Agent Interaction

```python
async def call_agent(runner, user_id, session_id, query):
    """Send a query to the agent and return the final response."""
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
    return final_response
```

### Running as a Script

```python
import asyncio

async def main():
    response = await call_agent(runner, "user_1", "session_1", "Hello!")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 11. Callbacks & Guardrails

Callbacks hook into the agent's execution at specific points to observe, customize, and control behavior.

### Callback Types

| Callback | When | Skip by returning | Replace by returning |
|:---------|:-----|:-------------------|:---------------------|
| `before_agent_callback` | Before agent runs | `types.Content` | — |
| `after_agent_callback` | After agent finishes | — | `types.Content` |
| `before_model_callback` | Before LLM call | `LlmResponse` | — |
| `after_model_callback` | After LLM response | — | `LlmResponse` |
| `before_tool_callback` | Before tool executes | `dict` | — |
| `after_tool_callback` | After tool returns | — | `dict` |

**Return `None`** to allow normal execution. **Return a value** to override/skip.

### Input Guardrail Example (`before_model_callback`)

```python
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from typing import Optional

def block_harmful_content(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Block requests containing harmful keywords."""
    last_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts:
            last_message = llm_request.contents[-1].parts[0].text

    blocked_keywords = ["hack", "exploit", "bypass"]
    if any(kw in last_message.lower() for kw in blocked_keywords):
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="I cannot process this request.")],
            )
        )
    return None  # Allow normal execution

agent = LlmAgent(
    name="SafeAgent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    before_model_callback=block_harmful_content
)
```

### Tool Argument Guardrail (`before_tool_callback`)

```python
from google.adk.tools import ToolContext

def validate_tool_args(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    """Block tool calls with invalid arguments."""
    if tool.name == "get_weather" and args.get("city", "").lower() == "forbidden_city":
        return {"error": "This city is not supported."}
    return None  # Allow tool execution

agent = LlmAgent(
    name="GuardedAgent",
    model="gemini-2.5-flash",
    tools=[get_weather],
    before_tool_callback=validate_tool_args
)
```

### Common Callback Patterns

1. **Guardrails & Policy Enforcement**: Inspect requests/args, block violations
2. **Dynamic State Management**: Read/write `callback_context.state` for context-aware behavior
3. **Logging & Monitoring**: Log at lifecycle points for observability
4. **Caching**: Cache LLM/tool results in state to avoid redundant calls
5. **Request/Response Modification**: Alter data before/after LLM/tool calls
6. **Conditional Skipping**: Bypass steps based on conditions

---

## 12. Model Configuration

ONLY use Google Gemini models. Do NOT use LiteLLM, OpenAI, Anthropic, Ollama, or any other non-Gemini model.

### Supported Models

| Model | Use Case |
|:------|:---------|
| `gemini-2.5-flash` | Fast, cost-effective — **default choice** for most agents |
| `gemini-2.5-pro` | More powerful — use for complex reasoning, planning, nuanced tasks |

### Usage

```python
# Default: fast and cost-effective
agent = Agent(
    model="gemini-2.5-flash",
    name="my_agent", ...
)

# For complex reasoning tasks
agent = Agent(
    model="gemini-2.5-pro",
    name="complex_agent", ...
)
```

### Fine-Tuning Generation Parameters

```python
from google.genai import types

agent = Agent(
    model="gemini-2.5-flash",
    name="tuned_agent",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,        # Lower = more deterministic
        max_output_tokens=500
    ),
    ...
)
```

---

## 13. Structured Output

### Using `output_schema`

Force the agent to produce structured JSON output:

```python
from pydantic import BaseModel, Field

class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital city.")
    population_estimate: str = Field(description="Estimated population.")

agent = LlmAgent(
    name="structured_agent",
    model="gemini-2.5-flash",
    instruction="Given a country, respond with JSON containing capital and population.",
    output_schema=CapitalOutput,  # Enforces JSON output
    output_key="result"           # Store in session state
    # Note: output_schema disables tool use and agent transfer
)
```

### Using `input_schema`

Define expected input format:

```python
class CountryInput(BaseModel):
    country: str = Field(description="The country name.")

agent = LlmAgent(
    name="agent",
    model="gemini-2.5-flash",
    input_schema=CountryInput,
    ...
)
```

### Using `generate_content_config` for JSON Mode

```python
from google.genai import types

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="json_agent",
    instruction="Always respond in JSON format.",
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2
    ),
    ...
)
```

---

## 14. Dev UI & Evaluation

### Development UI

ADK includes a built-in web UI for testing agents:

```bash
adk web my_agent_directory
```

This opens an interactive chat interface where you can test your agent, see tool calls, and debug.

### CLI Interaction

```bash
adk run my_agent_directory
```

### API Server

```bash
adk api_server my_agent_directory
```

### Evaluation

Evaluate agent performance using eval sets:

```bash
adk eval my_agent_directory my_agent_directory/eval_set.evalset.json
```

Eval set JSON format:

```json
[
  {
    "query": "What's the weather in Tokyo?",
    "expected_tool_use": ["get_weather"],
    "expected_intermediate_agent_actions": [],
    "reference": "The weather in Tokyo is..."
  }
]
```

---

## 15. Deployment

### Vertex AI Agent Engine

The fully managed option for production:

```python
from vertexai.preview import reasoning_engines
from vertexai import agent_engines

# Wrap agent for deployment
app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)

# Test locally first
session = app.create_session(user_id="test_user")
for event in app.stream_query(
    user_id="test_user", session_id=session.id, message="Hello"
):
    print(event)

# Deploy
remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=["google-cloud-aiplatform[adk,agent_engines]"]
)

# Use remotely
remote_session = remote_app.create_session(user_id="user_1")
for event in remote_app.stream_query(
    user_id="user_1",
    session_id=remote_session["id"],
    message="What's the weather?"
):
    print(event)

# Cleanup
remote_app.delete(force=True)
```

### Cloud Run

```bash
adk deploy cloud_run \
    --project=YOUR_PROJECT_ID \
    --region=us-central1 \
    my_agent_directory
```

Or using `gcloud`:

```bash
gcloud run deploy my-agent \
    --source=. \
    --region=us-central1 \
    --project=YOUR_PROJECT_ID
```

### Environment Variables for Deployment

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
```

---

## 16. Complete Examples

### Example 1: Simple Chatbot Agent

```python
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Define a tool
def get_greeting(name: str) -> str:
    """Returns a personalized greeting.

    Args:
        name: The name of the person to greet.
    Returns:
        A greeting string.
    """
    return f"Hello, {name}! Welcome to our service."

# Create agent
root_agent = Agent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="You are a friendly greeter. Use the get_greeting tool when someone introduces themselves.",
    tools=[get_greeting]
)

# Setup and run
async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="greeting_app", user_id="user_1", session_id="s1"
    )
    runner = Runner(agent=root_agent, app_name="greeting_app", session_service=session_service)

    message = types.Content(role='user', parts=[types.Part(text="Hi, I'm Alice!")])
    async for event in runner.run_async(user_id="user_1", session_id="s1", new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Multi-Agent Chatbot with Delegation

```python
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Define tools
def get_weather(city: str) -> dict:
    """Gets the weather for a city."""
    data = {"new york": "Sunny, 25°C", "london": "Cloudy, 15°C"}
    weather = data.get(city.lower())
    if weather:
        return {"status": "success", "report": f"Weather in {city}: {weather}"}
    return {"status": "error", "message": f"No data for {city}"}

def say_hello(name: str) -> str:
    """Greets the user by name."""
    return f"Hello {name}! How can I help you today?"

def say_goodbye(name: str) -> str:
    """Says goodbye to the user."""
    return f"Goodbye {name}! Have a great day!"

# Sub-agents
greeting_agent = LlmAgent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    instruction="You handle greetings. Use say_hello when someone introduces themselves.",
    description="Handles user greetings and introductions.",
    tools=[say_hello]
)

farewell_agent = LlmAgent(
    name="farewell_agent",
    model="gemini-2.5-flash",
    instruction="You handle farewells. Use say_goodbye when someone wants to leave.",
    description="Handles user farewells and goodbyes.",
    tools=[say_goodbye]
)

# Root coordinator agent
root_agent = LlmAgent(
    name="weather_bot",
    model="gemini-2.5-flash",
    instruction="""You are a weather bot coordinator.
- For weather questions, use the get_weather tool directly.
- For greetings, delegate to greeting_agent.
- For farewells, delegate to farewell_agent.""",
    description="Main weather bot that coordinates sub-agents.",
    tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent]
)

# Run conversation
async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="weather_app", user_id="user_1", session_id="s1"
    )
    runner = Runner(agent=root_agent, app_name="weather_app", session_service=session_service)

    queries = [
        "Hi, I'm Bob!",
        "What's the weather in New York?",
        "Thanks, goodbye Bob!"
    ]
    for query in queries:
        message = types.Content(role='user', parts=[types.Part(text=query)])
        async for event in runner.run_async(user_id="user_1", session_id="s1", new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"User: {query}")
                print(f"Bot: {event.content.parts[0].text}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Stateful Agent with Callbacks

```python
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools import ToolContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from typing import Optional
import asyncio

# Tool that uses state
def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Gets weather and remembers the last city checked."""
    tool_context.state["last_city"] = city
    data = {"new york": "Sunny, 25°C", "london": "Cloudy, 15°C"}
    weather = data.get(city.lower())
    if weather:
        return {"status": "success", "report": weather}
    return {"status": "error", "message": f"No data for {city}"}

# Input guardrail
def block_keywords(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Block messages containing blocked keywords."""
    if llm_request.contents and llm_request.contents[-1].parts:
        text = llm_request.contents[-1].parts[0].text.lower()
        if "politics" in text:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="I can only help with weather questions.")]
                )
            )
    return None

# Agent with state and guardrails
root_agent = Agent(
    name="stateful_weather_bot",
    model="gemini-2.5-flash",
    instruction="""You are a weather bot.
Use get_weather_stateful for weather queries.
If the user says 'last city', tell them the last city from state key 'last_city'.""",
    tools=[get_weather_stateful],
    before_model_callback=block_keywords
)

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="u1", session_id="s1",
        state={"preference": "celsius"}
    )
    runner = Runner(agent=root_agent, app_name="app", session_service=session_service)

    for query in ["Weather in London?", "What was my last city?", "Tell me about politics"]:
        msg = types.Content(role='user', parts=[types.Part(text=query)])
        async for event in runner.run_async(user_id="u1", session_id="s1", new_message=msg):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Q: {query}\nA: {event.content.parts[0].text}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Key Imports Reference

```python
# Environment (ALWAYS load .env at the top of every agent script)
from dotenv import load_dotenv
load_dotenv()

# Agents
from google.adk.agents import Agent, LlmAgent, BaseAgent
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext

# Runner & Sessions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.sessions import State  # For state prefixes

# Models
from google.adk.models import LlmResponse, LlmRequest

# Tools
from google.adk.tools import FunctionTool, google_search, load_memory
from google.adk.tools import agent_tool, ToolContext
from google.adk.tools.openapi_tool.openapi_spec_parser import OpenApiToolset
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.crewai_tool import CrewaiTool

# Memory
from google.adk.memory import InMemoryMemoryService

# Events
from google.adk.events import Event, EventActions

# Types (from google-genai)
from google.genai import types
from google.genai.types import Content, Part, GenerateContentConfig

# Pydantic (for schemas)
from pydantic import BaseModel, Field
```
