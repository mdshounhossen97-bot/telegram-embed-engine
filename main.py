import os
import re
import logging
from fastapi import FastAPI, Query
from telethon import TelegramClient
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
SESSION_NAME = os.environ.get("SESSION_NAME", "default_session")

app = FastAPI()
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    if not client.is_connected():
        await client.start(bot_token=BOT_TOKEN)
    
    logging.info("Bot started. Handshaking with channel...")
    # Bot ke baddho kora hobe channel-er hash cache korte
    async for dialog in client.iter_dialogs():
        if dialog.id == CHANNEL_ID:
            logging.info(f"Connected Successfully to: {dialog.title}")
            break

@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    search_query = tmdb_id
    if s is not None and e is not None:
        search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
    
    final_link = None
    try:
        # Direct channel search using ID
        async for message in client.iter_messages(CHANNEL_ID, search=search_query):
            if message.text:
                urls = re.findall(r'(https?://\S+)', message.text)
                if urls:
                    final_link = urls[0]
                    break
                    
        if not final_link:
            return "<h1>Link Not Found in Telegram! Check TMDB ID in Caption.</h1>"

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
                }});
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"<html><body style='background:#000;color:red;'><h1>Entity Error: {str(e)}</h1><p>Restart Render after posting a message in channel.</p></body></html>"
