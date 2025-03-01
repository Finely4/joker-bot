import discord
from discord.ext import commands
from discord import app_commands

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Test slash command for Active Developer Badge")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.mention}! 🎉")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
