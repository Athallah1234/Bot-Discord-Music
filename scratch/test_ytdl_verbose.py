import yt_dlp
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'verbose': True, # Enable verbose to see challenges
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def test():
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False))
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
