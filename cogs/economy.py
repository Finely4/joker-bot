import discord
from discord.ext import commands
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "balances"):
            self.bot.balances = {}  # Ensure balances dictionary exists

    @commands.command(name="commands")
    async def command_list(self, ctx):
        """Show available commands."""
        embed = discord.Embed(
            title="📜 Available Commands",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="**🔹 Important Commands**",
            value="!commands - Show this help menu",
            inline=False
        )
        embed.add_field(
            name="**💰 Economy Commands**",
            value="!beg - Try to get some coins (50% success)\n"
                  "!leaderboard - Show the top richest users",
            inline=False
        )
        embed.add_field(
            name="**🎰 Gamble Commands**",
            value="!coinflip - Flip a coin and bet your coins",
            inline=False
        )
        embed.set_footer(text="Use these commands to interact with the economy system!")
        await ctx.send(embed=embed)

    @commands.command(name="beg")
    @commands.cooldown(1, 150, commands.BucketType.user)
    async def beg(self, ctx):
        """Beg for coins. 50% success rate."""
        fail_responses = [
            "A rich man laughed at you.. FAILURE! 😆",
            "Another homeless man took your money.. (stop begging xd) 😔",
            "John Cena told you to stop begging. 🏋️‍♂️"
        ]

        if random.random() < 0.5:  # 50% fail chance
            response = random.choice(fail_responses)
            loss = random.randint(0, 1000) if response == fail_responses[1] else 0
            self.update_balance(ctx.author.id, -loss, "cash")

            embed = discord.Embed(
                title="Begging Failed!",
                description=f"{response} {'You lost **' + str(loss) + ' coins**!' if loss > 0 else ''}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        earnings = random.randint(1, 100)
        self.update_balance(ctx.author.id, earnings, "cash")

        embed = discord.Embed(
            title="Begging Success!",
            description=f"You begged and received **{earnings} coins**! 🤑",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    def update_balance(self, user_id, amount, account_type="cash"):
        """Update user balance safely."""
        user_id = str(user_id)  # Ensure user_id is a string for dict keys
        if user_id not in self.bot.balances or not isinstance(self.bot.balances[user_id], dict):
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}  # Fix incorrect entries
        self.bot.balances[user_id][account_type] += amount

    @commands.command(name="lb", aliases=["leaderboard"])
    async def lb(self, ctx):
        """Show the top 10 richest users."""
        print("Balances:", self.bot.balances)  # Debugging log

        if not self.bot.balances:
            await ctx.send("❌ No balances found. Start earning coins first!")
            return

        # Filter out invalid balances
        valid_balances = {
            user_id: balance for user_id, balance in self.bot.balances.items()
            if isinstance(balance, dict) and "cash" in balance and "bank" in balance
        }

        # Sort users by total balance (cash + bank)
        sorted_balances = sorted(
            valid_balances.items(),
            key=lambda x: x[1].get("cash", 0) + x[1].get("bank", 0),
            reverse=True
        )

        if not sorted_balances:
            await ctx.send("❌ No users have any coins yet!")
            return

        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="Top richest users:",
            color=discord.Color.purple()
        )

        medals = ["🥇", "🥈", "🥉"]  # Gold, Silver, Bronze
        default_medal = "🎖️"  # Medal for 4th place and beyond

        for idx, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
            try:
                user = await self.bot.fetch_user(int(user_id))  # Convert user_id to int
                total_balance = balance.get("cash", 0) + balance.get("bank", 0)
                medal = medals[idx - 1] if idx <= 3 else default_medal  # Assign medals
                embed.add_field(name=f"{medal} #{idx} {user.name}", value=f"**{total_balance:,} coins**", inline=False)
            except Exception as e:
                print(f"Error fetching user {user_id}: {e}")
                continue  # Skip this user and move to the next

        await ctx.send(embed=embed)

# Setup function to add this cog
async def setup(bot):
    await bot.add_cog(Economy(bot))
