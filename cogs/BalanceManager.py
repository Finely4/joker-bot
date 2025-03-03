import json
import os
import discord
from discord.ext import commands, tasks

class BalanceManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.balances = self.load_balances()  # Load balances on startup
        self.save_balances.start()  # Start the background task for saving balances

        # ✅ Register balance methods globally
        self.bot.get_balance = self.get_balance
        self.bot.update_balance = self.update_balance

    def load_balances(self):
        """Load balances from file, initializing to an empty dictionary if file doesn't exist."""
        if os.path.exists("balances.json"):
            try:
                with open("balances.json", "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding balances file: {e}")
                return {}  # Return empty dictionary if the file is corrupted
        return {}

    def get_balance(self, user_id, account_type="cash"):
        """Get the current balance of the user in either cash or bank."""
        user_id = str(user_id)
        if user_id not in self.bot.balances:
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}

        return self.bot.balances[user_id].get(account_type, 0)

    def update_balance(self, user_id, amount, account_type="cash"):
        """Update the balance of the user in either cash or bank."""
        user_id = str(user_id)

        if user_id not in self.bot.balances:
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}

        if account_type not in self.bot.balances[user_id]:
            print(f"Invalid account type {account_type} for user {user_id}")
            return

        self.bot.balances[user_id][account_type] += amount
        self.bot.balances_modified = True  # Mark balances as modified

    @tasks.loop(seconds=30)  # Adjust time interval to 30 seconds or more
    async def save_balances(self):
        """Save balances to file periodically."""
        if hasattr(self.bot, "balances_modified") and self.bot.balances_modified:
            try:
                with open("balances.json", "w") as f:
                    json.dump(self.bot.balances, f, indent=4)
                self.bot.balances_modified = False  # Reset the modified flag after saving
            except Exception as e:
                print(f"Error saving balances: {e}")

    @save_balances.before_loop
    async def before_save_balances(self):
        await self.bot.wait_until_ready()

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx):
        """Check your coin balance in cash and bank."""
        try:
            user_id = ctx.author.id
            cash_balance = self.get_balance(user_id, "cash")
            bank_balance = self.get_balance(user_id, "bank")

            embed = discord.Embed(
                title=f"{ctx.author.name}'s Balance 💰",
                color=discord.Color.gold()
            )
            embed.add_field(name="💵 Cash", value=f"{cash_balance:,} coins", inline=False)
            embed.add_field(name="🏦 Bank", value=f"{bank_balance:,} coins", inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in balance command: {e}")
            await ctx.send("An error occurred while retrieving your balance.")

    @commands.command(name="deposit")
    async def deposit(self, ctx, amount: str):
        """Deposit coins from cash into the bank."""
        user_id = ctx.author.id
        cash_balance = self.get_balance(user_id, "cash")

        if amount.lower() == "all":
            amount = cash_balance
        else:
            amount = int(float(amount.replace("k", "")) * 1000) if "k" in amount.lower() else int(amount)

        if amount <= 0:
            await ctx.send("❌ You must deposit a positive amount!")
            return
        if cash_balance < amount:
            await ctx.send("❌ You don't have enough coins in your cash balance to deposit that amount.")
            return

        self.update_balance(user_id, -amount, account_type="cash")
        self.update_balance(user_id, amount, account_type="bank")

        new_cash_balance = self.get_balance(user_id, "cash")
        new_bank_balance = self.get_balance(user_id, "bank")

        embed = discord.Embed(
            title="🏦 Deposit Successful!",
            description=f"✅ **{ctx.author.name}**, you have deposited **{amount:,}** coins into your bank!",
            color=discord.Color.green()
        )
        embed.add_field(name="💵 New Cash Balance", value=f"⏣ {new_cash_balance:,}", inline=False)
        embed.add_field(name="🏦 New Bank Balance", value=f"⏣ {new_bank_balance:,}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: str):
        """Withdraw coins from the bank to cash."""
        user_id = ctx.author.id
        bank_balance = self.get_balance(user_id, "bank")

        if amount.lower() == "all":
            amount = bank_balance
        else:
            amount = int(float(amount.replace("k", "")) * 1000) if "k" in amount.lower() else int(amount)

        if amount <= 0:
            await ctx.send("You must withdraw a positive amount!")
            return
        if bank_balance < amount:
            await ctx.send("You don't have enough coins in your bank balance to withdraw that amount.")
            return

        self.update_balance(user_id, -amount, account_type="bank")
        self.update_balance(user_id, amount, account_type="cash")
        await ctx.send(f"✅ {ctx.author.name}, you have withdrawn {amount:,} coins from your bank!")

    async def is_additional_owner(self, ctx):
        """Check if the user is the owner."""
        return ctx.author.id == 788507999748227073  # Replace with your actual owner ID

async def setup(bot):
    await bot.add_cog(BalanceManager(bot))
