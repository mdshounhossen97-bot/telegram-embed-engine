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
    search_query = tmdb_id
    if s is not None and e is not None:
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    final_link = None
    
    try:
        # Step 1: Entity manual resolve kora (Error fix korar jonno)
        entity = await client.get_input_entity(CHANNEL_ID)
        
        # Step 2: Message search kora
        async for message in client.iter_messages(entity, search=search_query):
            if message.text:
                found_urls = re.findall(r'(https?://\S+)', message.text)
                if found_urls:
                    final_link = found_urls[0]
                    break
    except Exception as e:
        return f"<html><body style='background:#000;color:red;'><h1>Entity Error: {str(e)}</h1></body></html>"
    
    if not final_link:
        return "<h1>Link Not Found in Telegram!</h1>"

    # Step 3: Pure Player (Jeta prothome apnar thik moto ashto)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
        <style>body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }} #player {{ width: 100vw; height: 100vh; }}</style>
    </head>
    <body>
        <div id="player"></div>
        <script>
            var art = new Artplayer({{
                container: '#player',
                url: '{final_link}',
                fullscreen: true,
                setting: true,
                hotkey: true,
            }});
        </script>
    </body>
    </html>
    """
