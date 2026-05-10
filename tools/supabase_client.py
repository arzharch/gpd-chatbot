from typing import Any, Dict, List

import anyio
from supabase import create_client

from config import settings


ALLOWED_FIELDS = {
    "id",
    "club_id",
    "name",
    "location",
    "type",
    "area",
    "description",
    "beds",
    "baths",
    "parking",
    "pool",
    "floor",
    "furnished",
    "zone_type",
    "road_access",
    "fsi",
    "image_urls",
    "instagram_url",
}


def _fetch_listings_sync() -> List[Dict[str, Any]]:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    response = client.table("listings").select(",".join(sorted(ALLOWED_FIELDS))).execute()
    data = response.data or []
    return [{key: row.get(key) for key in ALLOWED_FIELDS} for row in data]


def _upsert_session_sync(session_id: str) -> None:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    client.table("chat_sessions").upsert(
        {"session_id": session_id},
        on_conflict="session_id",
    ).execute()


def _insert_message_sync(
    session_id: str,
    role: str,
    content: str,
    metadata: Dict[str, Any] | None = None,
) -> None:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    payload = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "metadata": metadata or {},
    }
    client.table("chat_messages").insert(payload).execute()


def _fetch_messages_sync(session_id: str) -> List[Dict[str, Any]]:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    response = (
        client.table("chat_messages")
        .select("id,session_id,role,content,created_at,metadata")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return response.data or []


async def fetch_listings() -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_listings_sync)


async def upsert_session(session_id: str) -> None:
    await anyio.to_thread.run_sync(_upsert_session_sync, session_id)


async def insert_message(
    session_id: str,
    role: str,
    content: str,
    metadata: Dict[str, Any] | None = None,
) -> None:
    await anyio.to_thread.run_sync(_insert_message_sync, session_id, role, content, metadata)


async def fetch_messages(session_id: str) -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_messages_sync, session_id)
