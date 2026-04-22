import os
import re
import logging
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import HTMLResponse

# Logs check korar jonno setup
logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.on_event("startup")
async def startup_event():
    if not client.is_connected():
        await client.start(bot_token=BOT_TOKEN)

@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    try:
        # Step 1: Search Query toiri kora
        search_query = tmdb_id
        if s is not None and e is not None:
            search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
        
        logging.info(f"Searching for: {search_query} in Channel: {CHANNEL_ID}")

        # Step 2: Telegram theke link khunja
        final_link = None
        async for message in client.iter_messages(CHANNEL_ID, search=search_query):
            if message.text:
                found_urls = re.findall(r'(https?://\S+)', message.text)
                if found_urls:
                    final_link = found_urls[0]
                    break
        
        # Step 3: Link na pele error message dekhano
        if not final_link:
            return f"""
            <html><body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;">
                <div>
                    <h1 style="color:#ff4d4d;">Content Not Found!</h1>
                    <p>ID: {search_query} not found in Channel: {CHANNEL_ID}</p>
                    <p>Please check your Telegram Caption.</p>
                </div>
            </body></html>
            """

        # Step 4: Player UI
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
            <style>
                body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }}
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
                    hotkey: true,
                }});
            </script>
        </body>
        </html>
        """
    except Exception as e:
        # Internal Server Error hole ashol karon eikhane dekhabe
        return f"<html><body><h1>Internal Error: {str(e)}</h1></body></html>"
