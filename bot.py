import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
import asyncio
from dotenv import load_dotenv
from utils.logger import log

# Voice support libraries
try:
    import nacl
except ImportError:
    log.warning("PyNaCl is not installed, voice encryption might fail.")

try:
    import davey
except ImportError:
    log.warning("davey is not installed, modern voice support might fail.")

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')


class MusicBot(commands.Bot):
    def __init__(self):
        # Ensure Opus is loaded for voice
        if not discord.opus.is_loaded():
            # Standard locations for libopus
            locations = ['libopus-0.x64.dll', 'libopus-0.dll', 'opus']
            for loc in locations:
                try:
                    discord.opus.load_opus(loc)
                    log.info(f"Loaded Opus library from {loc}")
                    break
                except Exception:
                    continue
        
        if not discord.opus.is_loaded():
            log.warning("Could not load Opus library. Voice might not work.")

        intents = discord.Intents.default()
        intents.message_content = True  # Not strictly needed for pure slash, but good for some logs
        
        super().__init__(
            command_prefix=None, # Pure slash command bot
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Load cogs
        try:
            await self.load_extension('cogs.music')
            log.info("Successfully loaded cog: Music")
        except Exception as e:
            log.error(f"Failed to load cog: {e}")

        # Global error handler for slash commands
        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CommandOnCooldown):
                await interaction.response.send_message(f"Command is on cooldown. Try again in {error.retry_after:.2f}s.", ephemeral=True)
            else:
                log.error(f"Command Error: {error}")
                try:
                    if interaction.response.is_done():
                        await interaction.followup.send(f"An unexpected error occurred: `{error}`", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"An unexpected error occurred: `{error}`", ephemeral=True)
                except:
                    pass

        # Sync slash commands
        try:
            if GUILD_ID and GUILD_ID != "YOUR_GUILD_ID_HERE":
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info(f"Synced {len(synced)} slash commands to guild {GUILD_ID} (Instant).")
            else:
                synced = await self.tree.sync()
                log.info(f"Synced {len(synced)} slash commands globally (May take up to 1 hour).")
        except Exception as e:

            log.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        log.info(f'Logged in as {self.user} (ID: {self.user.id})')
        if debug_mode:
            log.info('DEBUG MODE IS ENABLED')
        log.info('------')
        
        # Set presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name="/play | Modern Music Bot"
            )
        )

async def main():
    if not TOKEN:
        log.critical("DISCORD_TOKEN not found in .env file!")
        return

    bot = MusicBot()
    
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot is shutting down...")
    except Exception as e:
        log.error(f"Fatal error: {e}")
