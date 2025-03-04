import random
import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class CrimeView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=30)  # Buttons expire after 30 seconds
        self.bot = bot
        self.user = user

        # Define two sets of crime options that randomly swap
        crime_sets = [
            [("Tax Evasion", "💰"), ("Armed Robbery", "🔫"), ("Bank Heist", "🏦")],
            [("Car Theft", "🚗"), ("Store Burglary", "🛒"), ("Cyber Fraud", "💻")]
        ]

        self.crimes = random.choice(crime_sets)  # Pick one set randomly

        for crime, emoji in self.crimes:
            self.add_item(CrimeButton(label=crime, emoji=emoji, bot=bot, user=user))

class CrimeButton(Button):
    def __init__(self, label, emoji, bot, user):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.primary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This isn't your crime attempt!", ephemeral=True)
            return

        await interaction.response.defer()
        user_id = str(self.user.id)

        # Define crime outcomes
        outcomes = [
            {"message": f"Your {self.label} was successful!", "amount": random.randint(500, 5000), "color": discord.Color.green()},
            {"message": f"Your {self.label} failed! You were fined!", "amount": -random.randint(500, 5000), "color": discord.Color.red()}
        ]
        outcome = random.choice(outcomes)
        amount = outcome["amount"]

        # Update balance using BalanceManager
        self.bot.update_balance(user_id, amount, account_type="cash")
        new_balance = self.bot.get_balance(user_id, "cash")

        embed = discord.Embed(
            title="Crime Attempt!",
            description=f"{outcome['message']} {'+' if amount > 0 else '-'} `{abs(amount):,}` coins!",
            color=outcome["color"]
        )
        embed.set_footer(text=f"Your new balance: {new_balance:,} coins")
        embed.set_author(name=self.user.display_name, icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        await interaction.followup.send(embed=embed)

        # Add cooldown
        self.bot.crime_cooldowns[self.user.id] = asyncio.get_event_loop().time() + 300

class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.crime_cooldowns = {}  # Store cooldowns

    @commands.command()
    async def crime(self, ctx):
        """Attempt a crime with a chance of success or failure."""
        user_id = ctx.author.id

        # Check cooldown
        if user_id in self.bot.crime_cooldowns:
            remaining = self.bot.crime_cooldowns[user_id] - asyncio.get_event_loop().time()
            if remaining > 0:
                minutes, seconds = divmod(int(remaining), 60)
                embed = discord.Embed(
                    title="Cooldown Active!",
                    description=f"You must wait **{minutes}m {seconds}s** before committing another crime.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        embed = discord.Embed(
            title="Choose Your Crime!",
            description="Click a button below to attempt a crime.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="You have 30 seconds to choose.")
        view = CrimeView(self.bot, ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Crime(bot))