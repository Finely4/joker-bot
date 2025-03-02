import random  # ✅ Added missing import
from discord.ext import commands
import discord


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["cf"])
    async def coinflip(self, ctx, arg1: str = None, arg2: str = None):
        """Gamble money by flipping a coin!"""
        if not arg1 or not arg2:
            embed = discord.Embed(
                title="❌ Incorrect Usage",
                description="To use this command, type:\n`!coinflip <heads/tails> <amount>`\nExample: `!coinflip heads 5000`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        user_id = str(ctx.author.id)

        # ✅ Ensure balances exist
        if not hasattr(self.bot, "balances"):
            self.bot.balances = {}

        balances = self.bot.balances  # Use the in-memory balance from economy.py

        valid_choices = {"h": "heads", "t": "tails", "head": "heads", "tail": "tails", "heads": "heads", "tails": "tails"}

        # Determine which argument is the bet amount and which is the choice
        if arg1.lower() in valid_choices:
            choice = valid_choices[arg1.lower()]
            amount_str = arg2
        elif arg2.lower() in valid_choices:
            choice = valid_choices[arg2.lower()]
            amount_str = arg1
        else:
            embed = discord.Embed(
                title="❌ Invalid Choice",
                description="Please choose **heads (h, head, heads)** or **tails (t, tail, tails)**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            bet_amount = int(amount_str.replace(",", ""))
            if bet_amount <= 0:  # ✅ Prevent negative or zero bets
                raise ValueError
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please enter a **valid number** greater than **0** for the bet amount.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if bet_amount < 1000:
            embed = discord.Embed(
                title="❌ Minimum Bet Not Met",
                description="The minimum bet amount is **⏣ 1,000**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if user_id not in balances or balances[user_id] < bet_amount:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description="You don't have enough money to place this bet!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        result = random.choice(["heads", "tails"])
        win = result == choice

        if win:
            winnings = bet_amount * 2
            balances[user_id] += winnings
            embed = discord.Embed(
                title="🎉 You Won!",
                description=f"The coin landed on **{result.capitalize()}**!\nYou won **⏣ {winnings:,}**!",
                color=discord.Color.green()
            )
        else:
            balances[user_id] -= bet_amount
            embed = discord.Embed(
                title="😢 You Lost!",
                description=f"The coin landed on **{result.capitalize()}**.\nYou lost **⏣ {bet_amount:,}**.",
                color=discord.Color.red()
            )

        self.bot.balances_modified = True  # ✅ Ensure balances get saved properly
        embed.add_field(name="💰 Current Balance", value=f"⏣ {balances[user_id]:,}", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Gamble(bot))
