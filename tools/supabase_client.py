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


async def fetch_listings() -> List[Dict[str, Any]]:
    return await anyio.to_thread.run_sync(_fetch_listings_sync)
