# Real Estate Agentic Chatbot

A production-ready, highly robust backend for an intelligent real estate concierge chatbot. Built with FastAPI, LangGraph, and Supabase, this system handles conversational requests, clarifies user intent, and autonomously searches a property database to recommend the best listings.

## System Architecture

Unlike traditional linear chatbots, this system leverages a fully **Agentic Architecture** via LangGraph. 

1. **Guardrails Layer**: Validates input against prompt injections and malicious content (SQLi, NSFW).
2. **LLM Supervisor**: An intelligent routing node that analyzes conversation state and dynamically chooses which tool to invoke using OpenAI function calling.
3. **Tool Actions**:
   - `query_properties`: Filters the database based on user criteria.
   - `ask_clarification`: Converses with the user for missing details.
   - `add_to_shortlist` / `remove_from_shortlist`: Manages a session-bound list of properties.
   - `compare_properties`: Weighs the pros and cons of shortlisted options.
   - `finalise_recommendation`: Prepares the final payload.
4. **Verifier**: A dedicated post-generation validation layer that scores the response, ensuring no PII leakage and high accuracy. If a response fails verification, the supervisor retries automatically.

## Key Features

- **Pydantic Driven:** Deep use of Pydantic models guarantees safe data structures across the state graph and API boundaries.
- **Fail-Safe & Verbose:** Strict `try/except` boundaries around tool executions and LLM calls mean the system degrades gracefully into a helpful "fallback" message rather than crashing, ensuring a seamless user experience.
- **Row Level Security (RLS):** Fully integrates with Supabase via dependency injected `ANON_KEY`, ensuring strict adherence to Postgres RLS policies and minimizing vulnerability footprints.

## Setup & Execution

### Requirements
- Python 3.10+
- A valid Supabase instance (with `listings`, `chat_sessions`, and `chat_messages` tables configured with proper RLS)
- OpenAI API Key

### Configuration

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

*Note: The system requires `gpt-4.1-nano-2025-04-14` by default for complex tool calling. You may override `MODEL_NAME` in the `.env` if necessary.*

### Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   fastapi dev main.py
   ```
3. The API will be available at `http://localhost:8000`. Refer to `APIDocumentation.md` for endpoint specifics.

### Testing

Run the included unit test suite to verify the integrity of the endpoints and dependency injection logic:
```bash
pytest tests/
```
