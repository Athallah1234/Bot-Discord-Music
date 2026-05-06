import asyncio
import discord
import yt_dlp
from discord.ext import commands
from utils.logger import log

# Silence useless bug reports messages
yt_dlp.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'force_ipv4': True,
    'cachedir': False,
    'extract_flat': 'in_playlist',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')
        self.requester = data.get('requester')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, requester=None):
        loop = loop or asyncio.get_event_loop()
        log.debug(f"Extracting info for URL/Query: {url}")
        data = await loop.run_in_executor(None, lambda *args, **kwargs: ytdl.extract_info(url, download=not stream))

        if not data:
            raise Exception(f"Could not find anything that matches `{url}`")

        if 'entries' in data:
            if not data['entries']:
                raise Exception(f"Could not find anything that matches `{url}`")
            # take first item from a playlist
            data = data['entries'][0]


        filename = data['url'] if stream else ytdl.prepare_filename(data)
        data['requester'] = requester
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop system, and manages the VoiceClient.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'loop_mode', '_alive')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = 0.5
        self.current = None
        self.loop_mode = 0  # 0 = None, 1 = Single, 2 = Queue
        self._alive = True

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while self._alive and not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout, cancel the player and disconnect...
                async with asyncio.timeout(300):  # 5 minutes
                    log.debug("Waiting for next song in queue...")
                    if self.loop_mode == 1 and self.current:

                        # Re-add the current song if looping single
                        source = await YTDLSource.from_url(self.current.source.webpage_url, loop=self.bot.loop, stream=True, requester=self.current.requester)
                        song = Song(source)
                    else:
                        song = await self.queue.get()
                        
                        if self.loop_mode == 2:
                            # Re-add to queue if looping queue
                            # Note: This is simplified. In a real queue loop, we'd need to keep the original list.
                            # For simplicity, we just put it back at the end.
                            source_copy = await YTDLSource.from_url(song.source.webpage_url, loop=self.bot.loop, stream=True, requester=song.requester)
                            await self.queue.put(Song(source_copy))

            except (asyncio.TimeoutError, asyncio.CancelledError):
                self._alive = False
                return self.destroy(self._guild)
            except Exception as e:
                log.error(f"Error in player loop: {e}")
                continue

            if not self._alive:
                break

            if not isinstance(song.source, YTDLSource):
                # Source was probably a stream (not downloaded)
                try:
                    source = await YTDLSource.from_url(song.source, loop=self.bot.loop, stream=True, requester=song.requester)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue
                song = Song(source)

            self.current = song
            song.source.volume = self.volume

            if not self._guild.voice_client:
                log.warning(f"Voice client disappeared in guild {self._guild.id}. Stopping player.")
                return self.destroy(self._guild)

            log.debug(f"Playing song: {song.source.title} in guild {self._guild.id}")
            self._guild.voice_client.play(song.source, after=lambda *args, **kwargs: self.bot.loop.call_soon_threadsafe(self.next.set))


            
            # Send Now Playing embed
            from modules.ui import PlayerView
            embed = self.create_embed()
            self.np = await self._channel.send(embed=embed, view=PlayerView(self))

            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            song.source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                if self.np:
                    await self.np.delete()
                    self.np = None
            except discord.HTTPException:
                pass


    def create_embed(self):
        """Create the Now Playing embed."""
        song = self.current
        embed = discord.Embed(title="Now Playing", description=f"[{song.source.title}]({song.source.webpage_url})", color=discord.Color.blurple())
        embed.set_thumbnail(url=song.source.thumbnail)
        
        duration = self.parse_duration(int(song.source.duration))
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Requested by", value=song.requester.mention, inline=True)
        
        loop_status = "None"
        if self.loop_mode == 1: loop_status = "🔂 Single"
        elif self.loop_mode == 2: loop_status = "🔁 Queue"
        embed.add_field(name="Loop Mode", value=loop_status, inline=True)
        
        embed.set_footer(text=f"Volume: {int(self.volume * 100)}%")
        return embed

    def parse_duration(self, duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration_str = []
        if days > 0: duration_str.append(f'{days}d')
        if hours > 0: duration_str.append(f'{hours}h')
        if minutes > 0: duration_str.append(f'{minutes}m')
        if seconds > 0: duration_str.append(f'{seconds}s')

        return ' '.join(duration_str)

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))
