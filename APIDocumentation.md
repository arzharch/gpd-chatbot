# Real Estate Agentic API Documentation

This document provides technical details on the API endpoints available in the GPD Chatbot backend. The application relies on an advanced agentic loop (LangGraph) integrated with OpenAI's API to understand, route, and execute tasks on behalf of the user.

## Base URL
Default: `http://localhost:8000`

---

## 1. Chat Endpoint

The core endpoint to interact with the conversational AI. The agent will read your query, manage session state, and perform actions like querying listings, saving properties to a shortlist, or asking for clarification.

- **URL:** `/chat`
- **Method:** `POST`
- **Content-Type:** `application/json`

### Request Payload (JSON)

| Field | Type | Description | Required |
| --- | --- | --- | --- |
| `query` | `string` | The user's input/message. | Yes |
| `session_id` | `string` | A unique identifier for the user's session to maintain conversation history. | Yes |

**Example Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "I am looking for a 3 bedroom apartment under 15 cr.",
  "session_id": "client_session_123"
}'
```

### Response Payload

The response varies depending on the action the agent decides to take. It will always return a JSON object with a `type` field.

#### Type 1: AI Reply
Returned when the agent wants to clarify details, greet the user, or explain something without returning final property IDs.

```json
{
  "type": "ai_reply",
  "message": "Great! I'd love to help you find an apartment. Do you have a preferred location in mind?"
}
```

#### Type 2: IDs Response
Returned when the agent finalizes a property recommendation.

```json
{
  "type": "ids",
  "ids": ["prop_101", "prop_102"],
  "message": "Here are some 3 BHK apartments under 15 Cr that match your criteria."
}
```

---

## 2. Session Messages Endpoint

Retrieve the entire message history for a specific session. Useful for rendering chat history on the client side.

- **URL:** `/sessions/{session_id}/messages`
- **Method:** `GET`

**Example Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/sessions/client_session_123/messages' \
  -H 'accept: application/json'
```

### Response Payload

Returns a JSON array of `ChatMessage` objects.

```json
[
  {
    "id": "msg_001",
    "session_id": "client_session_123",
    "role": "user",
    "content": "I am looking for a 3 bedroom apartment under 15 cr.",
    "created_at": "2026-05-11T12:00:00Z",
    "metadata": {}
  },
  {
    "id": "msg_002",
    "session_id": "client_session_123",
    "role": "assistant",
    "content": "Here are some 3 BHK apartments under 15 Cr that match your criteria.",
    "created_at": "2026-05-11T12:00:05Z",
    "metadata": {"ids": ["prop_101", "prop_102"]}
  }
]
```

## Error Handling

The API is built to be robust and highly fault-tolerant. 
- Validation errors (missing required fields) will return HTTP 422 Unprocessable Entity.
- Internal Agentic errors (e.g. LLM timeouts) are caught gracefully and returned as a standard `ai_reply` with an error explanation so the client app does not crash.
