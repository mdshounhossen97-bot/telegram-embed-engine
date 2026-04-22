import os
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import StreamingResponse, HTMLResponse

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Stream Logic
@app.get("/play/{tmdb_id}")
async def play_video(tmdb_id: str, s: int = None, e: int = None):
    # Search string toiri kora
    search_query = tmdb_id
    if s is not None and e is not None:
        # TV Series hole: "1399-S01-E01" formate khujbe
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    async for message in client.iter_messages(CHANNEL_ID, search=search_query):
        if message.video or message.document:
            async def file_sender():
                async for chunk in client.iter_download(message, chunk_size=1024*1024):
                    yield chunk
            return StreamingResponse(file_sender(), media_type="video/mp4")
    
    raise HTTPException(status_code=404, detail="Content not found")

# Embed Player Logic
@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    stream_url = f"/play/{tmdb_id}"
    if s and e:
        stream_url += f"?s={s}&e={e}"
        
    return f"""
    <html>
    <head>
        <title>Stream: {tmdb_id}</title>
        <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
        <style>body {{ margin: 0; background: #000; }} .artplayer-app {{ width: 100vw; height: 100vh; }}</style>
    </head>
    <body>
        <div class="artplayer-app"></div>
        <script>
            var art = new Artplayer({{
                container: '.artplayer-app',
                url: '{stream_url}',
                setting: true,
                fullscreen: true,
                pip: true,
                autoSize: true,
            }});
        </script>
    </body>
    </html>
    """
