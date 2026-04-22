import os
from fastapi import FastAPI, Response
from telethon import TelegramClient
from fastapi.responses import StreamingResponse

# Config (Variables Render theke ashbe)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = FastAPI()
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@app.get("/")
def home():
    return {"status": "Running", "message": "Telegram Embed Engine is Live!"}

@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    # Eikhane channel ID nirdisto kore dite hobe
    channel_id = int(os.environ.get("CHANNEL_ID"))
    
    async def file_sender():
        async for chunk in client.iter_download(await client.get_messages(channel_id, ids=message_id), chunk_size=1024*1024):
            yield chunk

    return StreamingResponse(file_sender(), media_type="video/mp4")
