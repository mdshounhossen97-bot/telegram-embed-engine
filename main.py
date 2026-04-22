import os
import asyncio
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import StreamingResponse, HTMLResponse

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = FastAPI()

# Stream optimizationer jonno client setup
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    await client.start(bot_token=BOT_TOKEN)

@app.get("/")
async def home():
    return {"status": "Active"}

@app.get("/play/{tmdb_id}")
async def play_video(tmdb_id: str, s: int = None, e: int = None):
    search_query = tmdb_id
    if s is not None and e is not None:
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    # Message khunje ber kora
    message = None
    async for msg in client.iter_messages(CHANNEL_ID, search=search_query):
        if msg.video or msg.document:
            message = msg
            break
    
    if not message:
        raise HTTPException(status_code=404, detail="Content not found")

    # Streaming logic with better chunking
    async def file_sender():
        # 512KB chunk size boro file-er jonno stable
        async for chunk in client.iter_download(message, chunk_size=512*1024):
            yield chunk

    return StreamingResponse(
        file_sender(), 
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"} # Eita player-ke seek/forward korte help kore
    )

@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    stream_url = f"/play/{tmdb_id}"
    if s and e:
        stream_url += f"?s={s}&e={e}"
        
    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
        <style>body {{ margin: 0; background: #000; overflow: hidden; }} .artplayer-app {{ width: 100vw; height: 100vh; }}</style>
    </head>
    <body>
        <div class="artplayer-app"></div>
        <script>
            var art = new Artplayer({{
                container: '.artplayer-app',
                url: '{stream_url}',
                type: 'mp4',
                setting: true,
                playbackRate: true,
                aspectRatio: true,
                fullscreen: true,
                pip: true,
                autoSize: true,
                fastForward: true,
                lock: true,
            }});
        </script>
    </body>
    </html>
    """
