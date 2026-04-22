import os
import re
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import HTMLResponse, RedirectResponse

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
    search_query = tmdb_id
    if s is not None and e is not None:
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    final_link = None
    async for message in client.iter_messages(CHANNEL_ID, search=search_query):
        if message.text:
            found_urls = re.findall(r'(https?://\S+)', message.text)
            if found_urls:
                final_link = found_urls[0]
                break
    
    if not final_link:
        return "<h1>Content Not Found in Telegram!</h1>"

    # Jodi link-er sheshe .mp4 thake, tobe Player-e dekhabo
    if any(ext in final_link.lower() for ext in ['.mp4', '.mkv', '.m3u8', '.webm']):
        return f"""
        <html>
        <head><script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script></head>
        <body style="margin:0;background:#000;"><div id="player" style="width:100vw;height:100vh;"></div>
        <script>
            new Artplayer({{ container: '#player', url: '{final_link}', fullscreen: true, setting: true }});
        </script>
        </body></html>
        """
    else:
        # Jodi direct link na hoy, tobe sorasori oi link-e Redirect korbe
        return RedirectResponse(url=final_link)
