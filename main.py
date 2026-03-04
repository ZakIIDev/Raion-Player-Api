from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
}

@app.get("/")
async def root():
    return {"status": "Algeria Music Backend Running"}

# Search YouTube
@app.get("/search")
async def search(q: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch10:{q}", download=False)

            results = []
            for entry in info["entries"]:
                results.append({
                    "id": entry["id"],
                    "title": entry["title"],
                    "thumbnail": entry["thumbnail"],
                    "duration": entry["duration"],
                })

            return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Best Audio Stream
@app.get("/audio/{video_id}")
async def get_audio(video_id: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )

            formats = info.get("formats", [])
            audio_formats = [
                f for f in formats if f.get("acodec") != "none"
            ]

            if not audio_formats:
                raise Exception("No audio format found")

            best_audio = sorted(
                audio_formats,
                key=lambda x: x.get("abr", 0),
                reverse=True
            )[0]

            return {
                "url": best_audio["url"],
                "bitrate": best_audio.get("abr"),
                "ext": best_audio.get("ext")
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
