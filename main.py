import os
import re
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import HTMLResponse

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    await client.start(bot_token=BOT_TOKEN)

@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    # TMDB ID check (Movie vs Series)
    search_query = tmdb_id
    if s is not None and e is not None:
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    final_link = None
    
    # Telegram channel-e caption search korbe
    async for message in client.iter_messages(CHANNEL_ID, search=search_query):
        if message.text:
            # Message-er moddhe thaka prothom link-ti (http/https) khuje nibe
            found_urls = re.findall(r'(https?://\S+)', message.text)
            if found_urls:
                final_link = found_urls[0]
                break
    
    if not final_link:
        return f"<html><body style='background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;'><h2>Content Not Found! Link missing for {search_query}</h2></body></html>"

    # Premium ArtPlayer Interface
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
        <style>
            body {{ margin: 0; background: #000; overflow: hidden; }}
            #player {{ width: 100vw; height: 100vh; }}
        </style>
    </head>
    <body>
        <div id="player"></div>
        <script>
            var art = new Artplayer({{
                container: '#player',
                url: '{final_link}',
                type: 'mp4',
                fullscreen: true,
                playbackRate: true,
                setting: true,
                pip: true,
                autoSize: true,
                autoMini: true,
                screenshot: true,
            }});
        </script>
    </body>
    </html>
    """
