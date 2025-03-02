import json
import os
import asyncio
import atexit  # ✅ Ensure save on force shutdown
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # ✅ Correct

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, application_id=1344729922328985670)

BALANCE_FILE = "balances.json"

# Load balances at startup into memory
def load_balances():
    """Load balances from file into memory."""
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save balances periodically & on shutdown
async def save_balances():
    """Save balances only when necessary to reduce I/O operations."""
    if bot.balances_modified:  # Only save if something changed
        async with asyncio.to_thread(open, BALANCE_FILE, "w") as f:
            json.dump(bot.balances, f, indent=4)
        bot.balances_modified = False  # Reset flag
        print("💾 Balances saved.")

# Attach balance functions to bot
bot.balances = load_balances()
bot.balances_modified = False  # Flag to track changes

# Background task to save balances every 5 minutes
@tasks.loop(minutes=5)
async def autosave_balances():
    await save_balances()

@bot.event
async def on_ready():
    autosave_balances.start()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Economy Crash"))

    print(f"✅ Logged in as {bot.user}.")
    print(f"🔍 Loaded Cogs: {list(bot.cogs.keys())}")

    # List all registered commands
    print(f"Registered commands: {[command.name for command in bot.commands]}")

    # Check if "crime" is in bot.commands
    if bot.get_command("crime"):
        print("✅ Crime command is registered!")
    else:
        print("❌ Crime command is NOT registered!")

@bot.event
async def on_disconnect():
    """Ensure balances are saved when bot disconnects."""
    await save_balances()
    print("💾 Balances saved before shutdown.")

# Ensure save even if bot is forcefully killed (CTRL+C, Railway shutdown)
atexit.register(lambda: asyncio.run(save_balances()))

# Command to reload a specific cog dynamically
@bot.command(name="reload", hidden=True)
@commands.is_owner()
async def reload(ctx, cog: str):
    """Reloads a cog dynamically."""
    cog_name = f"cogs.{cog}"
    try:
        await bot.unload_extension(cog_name)
        await bot.load_extension(cog_name)
        await ctx.send(f"🔄 Reloaded `{cog}` successfully!")
    except Exception as e:
        await ctx.send(f"❌ Error reloading `{cog}`: {e}")

async def main():
    async with bot:
        # Load cogs first
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"
                print(f"🔄 Loading: {cog_name}...")
                await bot.load_extension(cog_name)
                print(f"✅ Loaded: {cog_name}")

        print([command.name for command in bot.commands])

        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
