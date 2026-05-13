from typing import Any, Dict, List
import anyio
from fastapi import Depends
from supabase import create_client, Client
from config import settings

ALLOWED_FIELDS = {
    "id", "club_id", "name", "location", "type", "area",
    "description", "beds", "baths", "parking", "pool",
    "floor", "furnished", "zone_type", "road_access",
    "fsi", "image_urls", "instagram_url",
}

# Initialize clients globally to reuse connection pools and avoid WinError 10054 (Connection reset)
_READ_CLIENT: Client | None = None
_WRITE_CLIENT: Client | None = None

def get_read_client() -> Client:
    """Anon key client — honours RLS. Use for read-only access (listings)."""
    global _READ_CLIENT
    if _READ_CLIENT is None:
        _READ_CLIENT = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _READ_CLIENT

def get_write_client() -> Client:
    """Service role client — bypasses RLS. Use for session/message writes."""
    global _WRITE_CLIENT
    if _WRITE_CLIENT is None:
        _WRITE_CLIENT = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _WRITE_CLIENT

def _fetch_listings_sync(client: Client) -> List[Dict[str, Any]]:
    response = client.table("listings").select(",".join(sorted(ALLOWED_FIELDS))).execute()
    data = response.data or []
    return [{key: row.get(key) for key in ALLOWED_FIELDS} for row in data]

def _upsert_session_sync(client: Client, session_id: str) -> None:
    client.table("chat_sessions").upsert(
        {"session_id": session_id},
        on_conflict="session_id",
    ).execute()

def _insert_message_sync(
    client: Client,
    session_id: str,
    role: str,
    content: str,
    metadata: Dict[str, Any] | None = None,
) -> None:
    payload = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "metadata": metadata or {},
    }
    client.table("chat_messages").insert(payload).execute()

def _fetch_messages_sync(client: Client, session_id: str) -> List[Dict[str, Any]]:
    response = (
        client.table("chat_messages")
        .select("id,session_id,role,content,created_at,metadata")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return response.data or []

def _fetch_history_sync(client: Client, session_id: str, limit: int) -> List[Dict[str, Any]]:
    response = (
        client.table("chat_messages")
        .select("role,content")
        .eq("session_id", session_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )
    return response.data or []

def _fetch_session_metadata_sync(client: Client, session_id: str) -> Dict[str, Any]:
    response = (
        client.table("chat_sessions")
        .select("metadata")
        .eq("session_id", session_id)
        .single()
        .execute()
    )
    data = response.data or {}
    return data.get("metadata") or {}

def _update_session_summary_sync(client: Client, session_id: str, summary: str) -> None:
    metadata = _fetch_session_metadata_sync(client, session_id)
    metadata["summary"] = summary
    client.table("chat_sessions").update({"metadata": metadata}).eq("session_id", session_id).execute()

async def fetch_listings(client: Client) -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_listings_sync, client)

async def upsert_session(client: Client, session_id: str) -> None:
    await anyio.to_thread.run_sync(_upsert_session_sync, client, session_id)

async def insert_message(
    client: Client,
    session_id: str,
    role: str,
    content: str,
    metadata: Dict[str, Any] | None = None,
) -> None:
    await anyio.to_thread.run_sync(_insert_message_sync, client, session_id, role, content, metadata)

async def fetch_messages(client: Client, session_id: str) -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_messages_sync, client, session_id)

async def fetch_history(client: Client, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_history_sync, client, session_id, limit)

async def fetch_session_summary(client: Client, session_id: str) -> str:
    metadata = await anyio.to_thread.run_sync(_fetch_session_metadata_sync, client, session_id)
    summary = metadata.get("summary") if isinstance(metadata, dict) else None
    return summary or ""

async def update_session_summary(client: Client, session_id: str, summary: str) -> None:
    await anyio.to_thread.run_sync(_update_session_summary_sync, client, session_id, summary)

