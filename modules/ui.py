import discord
from discord.ui import View, Button

class PlayerView(View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.secondary)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player._guild.voice_client:
            return await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

        if self.player._guild.voice_client.is_paused():
            self.player._guild.voice_client.resume()
            await interaction.response.send_message("Resumed playback.", ephemeral=True)
        else:
            self.player._guild.voice_client.pause()
            await interaction.response.send_message("Paused playback.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player._guild.voice_client or not self.player._guild.voice_client.is_playing():
            return await interaction.response.send_message("Nothing is playing.", ephemeral=True)

        self.player._guild.voice_client.stop()
        await interaction.response.send_message("Skipped the current track.", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player._guild.voice_client:
            return await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

        self.player.queue._queue.clear()
        self.player._guild.voice_client.stop()
        await self.player._cog.cleanup(self.player._guild)
        await interaction.response.send_message("Stopped playback and cleared the queue.", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.loop_mode = (self.player.loop_mode + 1) % 3
        modes = ["None", "Single", "Queue"]
        
        # Update embed if something is playing
        if self.player.current:
            embed = self.player.create_embed()
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(f"Loop mode set to: **{modes[self.player.loop_mode]}**", ephemeral=True)
