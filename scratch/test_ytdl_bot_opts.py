import yt_dlp
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def test():
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False))
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
