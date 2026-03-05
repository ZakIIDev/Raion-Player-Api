from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from starlette.concurrency import run_in_threadpool
import yt_dlp
import functools
import os

app = FastAPI(title="Raion Player API", version="1.1.0")

# Check for cookies file
COOKIES_PATH = "cookies.txt" if os.path.exists("cookies.txt") else None

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "cookiefile": COOKIES_PATH,
    "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"],
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web", "ios"],
        }
    }
}

# --- Models ---

class SearchResult(BaseModel):
    id: str
    title: str
    thumbnail: str
    duration: int

class SearchResponse(BaseModel):
    results: List[SearchResult]

class AudioResponse(BaseModel):
    url: str
    bitrate: Optional[float]
    ext: str

# --- Helpers ---

def sync_extract_info(url: str, ydl_opts: dict):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@functools.lru_cache(maxsize=128)
def sync_search(query: str):
    """Synchronous search function to be cached."""
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        return ydl.extract_info(f"ytsearch10:{query}", download=False)

# --- Endpoints ---

@app.get("/")
async def root():
    return {"status": "Algeria Music Backend Running", "version": "1.1.0"}

@app.get("/search", response_model=SearchResponse)
async def search(q: str):
    try:
        # caching works on the sync function, we run it in a threadpool to avoid blocking
        info = await run_in_threadpool(sync_search, q)

        results = [
            SearchResult(
                id=entry["id"],
                title=entry["title"],
                thumbnail=entry["thumbnail"],
                duration=entry["duration"]
            )
            for entry in info.get("entries", [])
        ]

        return SearchResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{video_id}", response_model=AudioResponse)
async def get_audio(video_id: str):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        info = await run_in_threadpool(sync_extract_info, url, YDL_OPTS)

        formats = info.get("formats", [])
        # Prefer m4a audio if possible, then any audio
        audio_formats = [f for f in formats if f.get("acodec") != "none"]

        if not audio_formats:
            raise HTTPException(status_code=404, detail="No audio format found")

        # Sort by bitrate (handle None)
        best_audio = sorted(
            audio_formats,
            key=lambda x: (x.get("abr") or 0, x.get("ext") == "m4a"),
            reverse=True
        )[0]

        return AudioResponse(
            url=best_audio["url"],
            bitrate=best_audio.get("abr"),
            ext=best_audio.get("ext")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
