# src/services/musicbrainz_client.py
from __future__ import annotations

import time
from typing import Dict, List, Optional

import musicbrainzngs

from src.services.config import MB_APP_NAME, MB_APP_VERSION, MB_CONTACT_EMAIL

# --- Configure the client with a proper User-Agent (required by MusicBrainz) ---
musicbrainzngs.set_useragent(MB_APP_NAME, MB_APP_VERSION, MB_CONTACT_EMAIL)

# Optional: be nice and keep at ~1 request/second
_REQUEST_GAP_SECONDS = 1.1
_last_request_ts = 0.0


def _throttle() -> None:
    """Simple polite throttle so we don't hammer the API."""
    global _last_request_ts
    now = time.time()
    elapsed = now - _last_request_ts
    if elapsed < _REQUEST_GAP_SECONDS:
        time.sleep(_REQUEST_GAP_SECONDS - elapsed)
    _last_request_ts = time.time()


def find_artist_mbid(artist_name: str) -> Optional[str]:
    """
    Look up an artist by name and return the first matching MusicBrainz ID (MBID).
    Returns None if nothing is found.
    """
    if not artist_name.strip():
        return None

    _throttle()
    res = musicbrainzngs.search_artists(artist=artist_name.strip(), limit=1)
    artists = res.get("artist-list", [])
    if not artists:
        return None
    return artists[0].get("id")


def get_tribute_artists_for_original(original_mbid: str) -> List[Dict[str, str]]:
    """
    Given an original artist MBID, return a list of tribute artists.
    Each item is: {"mbid": "...", "name": "..."}

    Notes:
    - MusicBrainz stores artist-to-artist relationships in 'artist-relation-list'.
    - The relationship 'type' containing 'tribute' indicates a tribute relationship.
    - Direction can vary; we simply collect the 'other' artist when 'tribute' appears.
    """
    if not original_mbid:
        return []

    _throttle()
    details = musicbrainzngs.get_artist_by_id(original_mbid, includes=["artist-rels"])

    tribute_artists: List[Dict[str, str]] = []
    for rel in details.get("artist", {}).get("artist-relation-list", []):
        rel_type = (rel.get("type") or "").lower()
        if "tribute" not in rel_type:
            continue

        other = rel.get("artist")  # the related artist on the other side of the relation
        if not other:
            continue

        mbid = other.get("id")
        name = other.get("name")
        if not mbid or not name:
            continue

        tribute_artists.append({"mbid": mbid, "name": name})

    # De-duplicate by MBID (some data can have multiple edges)
    seen = set()
    unique = []
    for a in tribute_artists:
        if a["mbid"] not in seen:
            seen.add(a["mbid"])
            unique.append(a)

    return unique