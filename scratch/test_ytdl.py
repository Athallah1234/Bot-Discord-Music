import yt_dlp
print("yt-dlp version:", yt_dlp.version.__version__)
ytdl = yt_dlp.YoutubeDL({})
try:
    info = ytdl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
