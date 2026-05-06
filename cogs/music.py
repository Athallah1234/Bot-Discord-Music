import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from modules.player import MusicPlayer, Song, YTDLSource
from utils.logger import log


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, interaction):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[interaction.guild.id]
        except KeyError:
            # Create a simplified context
            class ContextMock:
                def __init__(self, interaction, bot, cog):
                    self.bot = bot
                    self.guild = interaction.guild
                    self.channel = interaction.channel
                    self.cog = cog
            
            player = MusicPlayer(ContextMock(interaction, self.bot, self))
            self.players[interaction.guild.id] = player
        return player


    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    @app_commands.command(name="help", description="Displays all available commands and their usage.")
    @app_commands.guild_only()
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎵 Modern Music Bot - Help Menu",
            description="Welcome to the ultimate music experience! Below are the available commands:",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="🚀 Getting Started",
            value="`/join` - Connect to your voice channel\n`/play [query]` - Play music from YouTube\n`/leave` - Disconnect from voice channel",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Playback Controls",
            value="`/pause` - Pause playback\n`/resume` - Resume playback\n`/skip` - Skip current track\n`/stop` - Stop & clear queue",
            inline=False
        )
        
        embed.add_field(
            name="📋 Queue & Info",
            value="`/queue` - Show current queue\n`/nowplaying` - Show current song info\n`/volume [1-100]` - Change volume",
            inline=False
        )
        
        embed.set_footer(text="Tip: Use the buttons under the 'Now Playing' message for quick controls!")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join", description="Connects the bot to a voice channel.")

    @app_commands.guild_only()
    async def join(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if not interaction.user.voice:
            return await interaction.followup.send("You are not connected to a voice channel.", ephemeral=True)
        
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect(self_deaf=True)
        
        await interaction.followup.send(f"Connected to **{channel.name}**")


    @app_commands.command(name="play", description="Plays a song from YouTube or searches for one.")
    @app_commands.guild_only()
    @app_commands.describe(query="The song title or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        if not interaction.user.voice:

            return await interaction.followup.send("You are not connected to a voice channel.", ephemeral=True)

        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect(self_deaf=True)

        player = self.get_player(interaction)



        try:
            # We don't download, just extract
            source = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True, requester=interaction.user)
        except Exception as e:
            log.error(f"Error extracting song: {e}")
            return await interaction.followup.send(f"An error occurred: `{e}`")

        song = Song(source)
        await player.queue.put(song)
        
        if player.current:
            await interaction.followup.send(f"Added **{source.title}** to the queue.")
        else:
            await interaction.followup.send(f"Now playing **{source.title}**")

    @app_commands.command(name="pause", description="Pauses the current song.")
    @app_commands.guild_only()
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        
        vc.pause()
        await interaction.response.send_message("Paused ⏸️")

    @app_commands.command(name="resume", description="Resumes the paused song.")
    @app_commands.guild_only()
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_paused():
            return await interaction.response.send_message("Nothing is paused.", ephemeral=True)
        
        vc.resume()
        await interaction.response.send_message("Resumed ▶️")

    @app_commands.command(name="skip", description="Skips the current song.")
    @app_commands.guild_only()
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        
        vc.stop()
        await interaction.response.send_message("Skipped ⏭️")

    @app_commands.command(name="stop", description="Stops playback and clears the queue.")
    @app_commands.guild_only()
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.followup.send("I'm not in a voice channel.", ephemeral=True)

        player = self.players.get(interaction.guild.id)
        if player:
            # Properly empty the queue
            while not player.queue.empty():
                try:
                    player.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        vc.stop()
        await self.cleanup(interaction.guild)
        await interaction.followup.send("Stopped and cleared everything ⏹️")


    @app_commands.command(name="queue", description="Shows the current music queue.")
    @app_commands.guild_only()
    async def queue_info(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id)
        if not player or player.queue.empty():
            return await interaction.response.send_message("The queue is currently empty.", ephemeral=True)

        upcoming = list(player.queue._queue)
        if not upcoming:
            return await interaction.response.send_message("The queue is currently empty.", ephemeral=True)

        fmt = "\n".join([f"`{i+1}.` **{s.source.title}** | <@{s.requester.id}>" for i, s in enumerate(upcoming[:10])])
        
        embed = discord.Embed(
            title=f"Queue for {interaction.guild.name}", 
            description=f"**Currently Playing:**\n{player.current.source.title if player.current else 'None'}\n\n**Upcoming:**\n{fmt}", 
            color=discord.Color.blurple()
        )
        
        if len(upcoming) > 10:
            embed.set_footer(text=f"And {len(upcoming) - 10} more tracks...")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Shuffles the current music queue.")
    @app_commands.guild_only()
    async def shuffle_queue(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id)
        if not player or player.queue.empty():
            return await interaction.response.send_message("The queue is empty.", ephemeral=True)

        import random
        upcoming = list(player.queue._queue)
        random.shuffle(upcoming)
        
        # Clear and refill queue
        while not player.queue.empty():
            player.queue.get_nowait()
        
        for song in upcoming:
            await player.queue.put(song)
            
        await interaction.response.send_message("Queue shuffled! 🔀")

    @app_commands.command(name="remove", description="Removes a specific song from the queue.")
    @app_commands.guild_only()
    @app_commands.describe(index="The index of the song to remove")
    async def remove_song(self, interaction: discord.Interaction, index: int):
        player = self.players.get(interaction.guild.id)
        if not player or player.queue.empty():
            return await interaction.response.send_message("The queue is empty.", ephemeral=True)

        upcoming = list(player.queue._queue)
        if index < 1 or index > len(upcoming):
            return await interaction.response.send_message(f"Invalid index. Please choose between 1 and {len(upcoming)}.", ephemeral=True)

        removed = upcoming.pop(index - 1)
        
        # Clear and refill
        while not player.queue.empty():
            player.queue.get_nowait()
            
        for song in upcoming:
            await player.queue.put(song)

        await interaction.response.send_message(f"Removed **{removed.source.title}** from the queue.")

    @app_commands.command(name="nowplaying", description="Shows info about the current song.")
    @app_commands.guild_only()
    async def now_playing(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id)
        if not player or not player.current:
            return await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

        embed = player.create_embed()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Changes the player volume.")
    @app_commands.guild_only()
    @app_commands.describe(volume="Volume level (1-100)")
    async def change_volume(self, interaction: discord.Interaction, volume: int):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

        if not 0 < volume <= 100:
            return await interaction.response.send_message("Volume must be between 1 and 100.", ephemeral=True)

        player = self.get_player(interaction)
        player.volume = volume / 100
        if vc.source:
            vc.source.volume = volume / 100

        await interaction.response.send_message(f"Volume set to **{volume}%**")

    @app_commands.command(name="leave", description="Disconnects from the voice channel.")
    @app_commands.guild_only()
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

        await self.cleanup(interaction.guild)
        await interaction.response.send_message("Disconnected 👋")


async def setup(bot):
    await bot.add_cog(Music(bot))
