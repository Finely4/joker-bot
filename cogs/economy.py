import discord
from discord.ext import commands
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "balances"):
            self.bot.balances = {}  # Ensure balances dictionary exists
        self.cooldowns = commands.CooldownMapping.from_cooldown(1, 150, commands.BucketType.user)  # 150s cooldown

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
                  "!leaderboard (!lb) - Show the top richest users",
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
    async def beg(self, ctx):
        """Beg for coins. 50% success rate."""
        bucket = self.cooldowns.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            remaining_time = int(retry_after)
            embed = discord.Embed(
                title="⏳ Cooldown!",
                description=f"You must wait **{remaining_time} seconds** before begging again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        fail_responses = [
            "A rich man laughed at you.. FAILURE! 😆",
            "Another homeless man took your money.. (stop begging xd) 😔",
            "John Cena told you to stop begging. 🏈"
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

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Display the top 10 richest users based on cash balance only."""
        print("🔍 Debug: leaderboard command triggered!")

        if not hasattr(self.bot, "balances") or not self.bot.balances:
            print(f"⚠️ Warning: No balance data found! balances={self.bot.balances}")
            await ctx.send("🚨 No balance data found!")
            return

        for user_id in list(self.bot.balances.keys()):
            if not isinstance(self.bot.balances[user_id], dict):
                print(f"⚠️ Fixing invalid balance entry for {user_id}: {self.bot.balances[user_id]}")
                self.bot.balances[user_id] = {"cash": int(self.bot.balances[user_id]), "bank": 0}

        print(f"📊 Debug: Cleaned balances -> {self.bot.balances}")

        try:
            sorted_balances = sorted(
                self.bot.balances.items(),
                key=lambda x: x[1].get("cash", 0),  # Only consider cash balance
                reverse=True
            )
        except Exception as e:
            print(f"❌ Error sorting balances: {e}")
            await ctx.send(f"🚨 Sorting error: {e}")
            return

        if not sorted_balances:
            print("⚠️ Warning: No users have balances yet!")
            await ctx.send("🚨 No users have balances yet!")
            return

        print(f"🏆 Debug: Sorted balances -> {sorted_balances[:10]}")

        medal_emojis = ["🥇", "🥈", "🥉"]  # Top 3 fixed medals
        random_medals = ["🏅", "🎖️", "🏵️", "🌟", "🔹"]  # Random medals for 4th place and beyond

        leaderboard_text = "\n".join(
            [
                f"{medal_emojis[idx] if idx < 3 else random.choice(random_medals)} <@{user_id}> - {data['cash']:,} coins"
                for idx, (user_id, data) in enumerate(sorted_balances[:10])
            ]
        )

        if not leaderboard_text:
            print("⚠️ Warning: leaderboard_text is empty!")
            await ctx.send("🚨 Something went wrong generating the leaderboard!")
            return

        print("✅ Debug: Leaderboard generated successfully!")

        embed = discord.Embed(title="🏆 Richest Users", description=leaderboard_text, color=discord.Color.gold())
        await ctx.send(embed=embed)

    def update_balance(self, user_id, amount, account_type="cash"):
        """Update user balance safely and fix incorrect entries."""
        user_id = str(user_id)  # Ensure user_id is a string for dict keys

        if user_id not in self.bot.balances or not isinstance(self.bot.balances[user_id], dict):
            print(f"⚠️ Fixing balance for {user_id}, resetting to default structure.")
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}  # Reset incorrect entries

        if "cash" not in self.bot.balances[user_id]:
            self.bot.balances[user_id]["cash"] = 0
        if "bank" not in self.bot.balances[user_id]:
            self.bot.balances[user_id]["bank"] = 0

        self.bot.balances[user_id][account_type] += amount

async def setup(bot):
    await bot.add_cog(Economy(bot))