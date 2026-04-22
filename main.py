import os
import re
import logging
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from fastapi.responses import HTMLResponse

# Logs setup
logging.basicConfig(level=logging.INFO)

# Environment Variables theke data neya
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
    try:
        # Channel entity-ke force fetch kora jate PeerChannel Error na ashe
        await client.get_entity(CHANNEL_ID)
        logging.info(f"Successfully connected to Channel: {CHANNEL_ID}")
    except Exception as e:
        logging.error(f"Failed to connect to channel: {e}")

@app.get("/embed/{tmdb_id}", response_class=HTMLResponse)
async def embed_player(tmdb_id: str, s: int = Query(None), e: int = Query(None)):
    try:
        # Step 1: Search Query toiri (Movie ba Series er jonno)
        search_query = tmdb_id
        if s is not None and e is not None:
            search_query = f"{tmdb_id}-S{s:02d}-E{e:02d}"
        
        logging.info(f"Searching for: {search_query}")

        # Step 2: Telegram Channel theke Link khunja
        final_link = None
        async for message in client.iter_messages(CHANNEL_ID, search=search_query):
            if message.text:
                # Caption theke link ber kora
                found_urls = re.findall(r'(https?://\S+)', message.text)
                if found_urls:
                    final_link = found_urls[0]
                    # Google Drive link hole confirm parameter add kora (Bypass scan)
                    if "drive.google.com" in final_link or "docs.google.com" in final_link:
                        if "confirm=t" not in final_link:
                            final_link += "&confirm=t"
                    break
        
        # Step 3: Link na paoa gele error message
        if not final_link:
            return f"""
            <html><body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;">
                <div>
                    <h1 style="color:#ff4d4d;">404 - Not Found</h1>
                    <p>Could not find link for: <b>{search_query}</b></p>
                    <p>Make sure you posted it in Telegram Channel: {CHANNEL_ID}</p>
                </div>
            </body></html>
            """

        # Step 4: ArtPlayer UI
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
                    screenshot: true,
                    hotkey: true,
                    lock: true,
                }});

                // Video load korte error hole link redirect hobe
                art.on('error', function() {{
                    console.log("ArtPlayer Error: Falling back to direct link");
                    window.location.href = "{final_link}";
                }});
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"<html><body style='background:#000;color:#fff;'><h1>Server Error: {str(e)}</h1></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
