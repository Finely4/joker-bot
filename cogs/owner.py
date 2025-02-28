import discord
import json
from discord.ext import commands

BALANCE_FILE = "user_balances.json"

def load_balances():
    try:
        with open(BALANCE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w") as file:
        json.dump(balances, file, indent=4)

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_balance(self, user_id: str, amount: int):
        balances = load_balances()
        balances[user_id] = balances.get(user_id, 0) + amount
        save_balances(balances)
        return balances[user_id]

    @commands.command(name="addbalance")
    @commands.is_owner()
    async def add_balance(self, ctx, member: discord.Member, amount: str):
        """Adds money to a user's balance (Owner Only)"""
        try:
            amount = int(amount.replace(",", ""))  # Convert comma-separated input to an integer
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Invalid amount! Please enter a **valid number**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if amount < 0:
            embed = discord.Embed(
                title="❌ Error",
                description="Amount must be **positive**!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        new_balance = self.update_balance(str(member.id), amount)
        embed = discord.Embed(
            title="✅ Balance Added",
            description=f"Added **⏣ {amount:,}** to {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="New Balance", value=f"⏣ {new_balance:,}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="removebalance")
    @commands.is_owner()
    async def remove_balance(self, ctx, member: discord.Member, amount: str):
        """Removes money from a user's balance (Owner Only)"""
        try:
            amount = int(amount.replace(",", ""))  # Convert comma-separated input to an integer
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Invalid amount! Please enter a **valid number**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if amount < 0:
            embed = discord.Embed(
                title="❌ Error",
                description="Amount must be **positive**!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        balances = load_balances()
        user_id = str(member.id)

        if user_id not in balances or balances[user_id] < amount:
            embed = discord.Embed(
                title="❌ Error",
                description="User does not have enough **balance**!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        new_balance = self.update_balance(user_id, -amount)
        embed = discord.Embed(
            title="✅ Balance Removed",
            description=f"Removed **⏣ {amount:,}** from {member.mention}.",
            color=discord.Color.orange()
        )
        embed.add_field(name="New Balance", value=f"⏣ {new_balance:,}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="clearbalance")
    @commands.is_owner()
    async def clear_balance(self, ctx, member: discord.Member):
        """Clears a user's balance (Owner Only)"""
        balances = load_balances()
        user_id = str(member.id)

        if user_id not in balances or balances[user_id] == 0:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{member.mention} already has **0** balance!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        balances[user_id] = 0
        save_balances(balances)

        embed = discord.Embed(
            title="✅ Balance Cleared",
            description=f"{member.mention}'s balance has been reset to **⏣ 0**.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))
