import discord
from discord.ext import commands
import time
import json

DATA_FILE = "daily_data.json"
BALANCES_FILE = "balances.json"

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_data()
        self.load_balances()

    def load_data(self):
        """Load daily streaks and last claimed times from a file."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.bot.daily_streaks = data.get("daily_streaks", {})
                self.bot.last_claimed = data.get("last_claimed", {})
        except FileNotFoundError:
            self.bot.daily_streaks = {}
            self.bot.last_claimed = {}

    def save_data(self):
        """Save daily streaks and last claimed times to a file."""
        data = {
            "daily_streaks": self.bot.daily_streaks,
            "last_claimed": self.bot.last_claimed,
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

    def load_balances(self):
        """Load user balances from a file."""
        try:
            with open(BALANCES_FILE, "r") as f:
                self.bot.balances = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.bot.balances = {}

    def save_balances(self):
        """Save user balances to a file."""
        with open(BALANCES_FILE, "w") as f:
            json.dump(self.bot.balances, f)

    @commands.command(name="daily")
    async def daily(self, ctx):
        """Claim your daily reward, increasing by 100K per day."""
        user_id = str(ctx.author.id)
        current_time = time.time()

        last_claim = float(self.bot.last_claimed.get(user_id, 0))
        streak = int(self.bot.daily_streaks.get(user_id, 0))

        time_since_last = current_time - last_claim
        remaining_time = int(86400 - time_since_last)

        if time_since_last < 86400:  # 24 hours cooldown
            embed = discord.Embed(
                title="⏳ Daily Reward Cooldown",
                description=f"You can claim your next daily reward in **{remaining_time // 3600}h {(remaining_time % 3600) // 60}m {remaining_time % 60}s**.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        # Increase streak and calculate reward
        streak += 1
        reward = 100000 * streak
        self.bot.daily_streaks[user_id] = streak
        self.bot.last_claimed[user_id] = current_time
        self.save_data()  # Save cooldown and streak

        # Update user's balance (Depositing directly into the bank)
        if user_id not in self.bot.balances:
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}
        self.bot.balances[user_id]["bank"] += reward
        self.save_balances()  # Save updated balances

        embed = discord.Embed(
            title="🎉 Daily Reward Claimed!",
            description=f"You claimed **{reward:,} coins**! 💰 (Deposited in your bank)",
            color=discord.Color.green()
        )
        embed.add_field(name="🔥 Streak Bonus!", value=f"You're on a **{streak}-day streak!** Keep it up!", inline=False)
        embed.set_footer(text="Come back every day to increase your reward!")

        await ctx.send(embed=embed)

# Setup function to add this cog
async def setup(bot):
    await bot.add_cog(Daily(bot))