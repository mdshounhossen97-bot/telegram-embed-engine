import os
from fastapi import FastAPI, HTTPException
from telethon import TelegramClient
from fastapi.responses import StreamingResponse, HTMLResponse

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@app.get("/")
def home():
    return {"status": "Active", "message": "TMDB Movie Engine Live!"}

# TMDB ID diye video stream korar endpoint
@app.get("/play/{tmdb_id}")
async def play_by_tmdb(tmdb_id: str):
    # Channel-e search korbe caption-e oi TMDB ID ache kina
    async for message in client.iter_messages(CHANNEL_ID, search=tmdb_id):
        if message.video or message.document:
            msg_id = message.id
            
            # Direct link generate hobe (Amader player-e chalanor jonno)
            async def file_sender():
                async for chunk in client.iter_download(message, chunk_size=1024*1024):
                    yield chunk
            
            return StreamingResponse(file_sender(), media_type="video/mp4")
    
    raise HTTPException(status_code=404, detail="Movie not found in Telegram Channel")

# Premium Player Interface (ArtPlayer)
@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str):
    stream_url = f"/play/{tmdb_id}"
    return f"""
    <html>
    <head>
        <title>Premium Player</title>
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
                playbackRate: true,
                aspectRatio: true,
                fullscreen: True,
                pip: true,
                autoSize: true,
            }});
        </script>
    </body>
    </html>
    """
