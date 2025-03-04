import json
import os
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import signal

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
BALANCE_FILE = "balances.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Ensure this is enabled in Developer Portal

bot = commands.Bot(command_prefix="!", intents=intents, application_id=1344729922328985670)
bot.balances = {}
bot.balances_modified = False

def load_balances():
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("⚠️ Error loading balances.json. Using empty balances.")
            return {}
    return {}

async def save_balances():
    if bot.balances_modified:
        print("💾 Saving balances...")
        with open(BALANCE_FILE, "w") as f:
            json.dump(bot.balances, f, indent=4)
        bot.balances_modified = False
        print("✅ Balances saved successfully.")

@tasks.loop(seconds=1)  # Save every second
async def autosave_balances():
    await save_balances()

@bot.event
async def on_ready():
    bot.balances = load_balances()

    if not autosave_balances.is_running():
        autosave_balances.start()

    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Economy Crash"))

@bot.event
async def on_disconnect():
    await save_balances()
    print("💾 Balances saved before disconnect.")

async def shutdown_handler():
    print("⚠️ Shutdown Detected...")
    await save_balances()
    autosave_balances.cancel()
    print("✅ Balances successfully saved before shutdown.")

if os.name != "nt":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown_handler()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown_handler()))

@bot.command(name="save")
async def save(ctx):
    await save_balances()
    await ctx.send("💾 Balances have been saved!")

async def main():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"✅ Loaded {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {e}")

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await shutdown_handler()

if __name__ == "__main__":
    asyncio.run(main())
