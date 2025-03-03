import random
from discord.ext import commands
import discord


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["cf"])
    async def coinflip(self, ctx, arg1: str = None, arg2: str = None):
        """Gamble money by flipping a coin!"""
        try:
            print(f"Coinflip command triggered by {ctx.author.name}")

            balance_cog = self.bot.get_cog("BalanceManager")
            if not balance_cog:
                print("Error: BalanceManager cog is not loaded")
                await ctx.send("❌ Balance system is not available. Please contact an admin.")
                return

            if not arg1 or not arg2:
                embed = discord.Embed(
                    title="❌ Incorrect Usage",
                    description="To use this command, type:\n`!coinflip <heads/tails> <amount>`\nExample: `!coinflip heads 5000`",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            user_id = str(ctx.author.id)
            cash_balance = balance_cog.get_balance(user_id, "cash")

            valid_choices = {"h": "heads", "t": "tails", "head": "heads", "tail": "tails", "heads": "heads", "tails": "tails"}

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
                if amount_str.lower() == "all":
                    bet_amount = cash_balance
                    if bet_amount == 0:
                        raise ValueError("You don't have any money to bet.")
                else:
                    amount_str = amount_str.replace(",", "")
                    bet_amount = int(float(amount_str.replace("k", "")) * 1000) if "k" in amount_str.lower() else int(amount_str)
                    if bet_amount <= 0:
                        raise ValueError("Bet amount must be greater than 0.")
            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Amount",
                    description=f"Error: {e}\nPlease enter a **valid number** greater than **0** for the bet amount, or type `all` to bet your entire balance.",
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

            if cash_balance < bet_amount:
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
                balance_cog.update_balance(user_id, winnings, "cash")
                embed = discord.Embed(
                    title="🎉 You Won!",
                    description=f"The coin landed on **{result.capitalize()}**!\nYou won **⏣ {winnings:,}**!",
                    color=discord.Color.green()
                )
            else:
                balance_cog.update_balance(user_id, -bet_amount, "cash")
                embed = discord.Embed(
                    title="😢 You Lost!",
                    description=f"The coin landed on **{result.capitalize()}**.\nYou lost **⏣ {bet_amount:,}**.",
                    color=discord.Color.red()
                )

            embed.add_field(name="💰 Current Balance", value=f"⏣ {balance_cog.get_balance(user_id, 'cash'):,}", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error in !coinflip command: {str(e)}")
            embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred while processing your request. Please try again later.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Gamble(bot))
