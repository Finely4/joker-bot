import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Slash Command `/ping`
    @app_commands.command(name="ping", description="Check the bot's ping.")
    async def ping(self, interaction: discord.Interaction):
        """Responds with the bot's ping."""
        latency = round(self.bot.latency * 1000)  # Convert latency to milliseconds
        await interaction.response.send_message(f"🏓 Pong! The bot's latency is {latency}ms.")

async def setup(bot):
    await bot.add_cog(Ping(bot))
