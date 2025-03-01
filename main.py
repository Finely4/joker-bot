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

print(f"TOKEN: {TOKEN}")  # Debugging step (remove this later)

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

BALANCE_FILE = "balances.json"

# Load balances at startup into memory
def load_balances():
    """Load balances from file into memory."""
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save balances periodically & on shutdown
def save_balances():
    """Save balances only when necessary to reduce I/O operations."""
    if bot.balances_modified:  # Only save if something changed
        with open(BALANCE_FILE, "w") as f:
            json.dump(bot.balances, f, indent=4)
        bot.balances_modified = False  # Reset flag
        print("💾 Balances saved.")

# Attach balance functions to bot
bot.balances = load_balances()
bot.balances_modified = False  # Flag to track changes

# Background task to save balances every 5 minutes
@tasks.loop(minutes=5)
async def autosave_balances():
    save_balances()

# Load cogs dynamically
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                print(f"🔄 Loading: {cog_name}...")
                await bot.load_extension(cog_name)
                print(f"✅ Loaded: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {e}")

# Event: On bot ready
@bot.event
async def on_ready():
    autosave_balances.start()
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()  # Sync all slash commands
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

# ✅ Event: On shutdown (triggers when bot is stopped properly)
@bot.event
async def on_shutdown():
    save_balances()
    print("💾 Balances saved before shutdown.")

# ✅ Ensure save even if bot is forcefully killed (CTRL+C, Railway shutdown)
atexit.register(save_balances)

# Run the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
