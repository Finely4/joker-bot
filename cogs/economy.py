import discord
from discord.ext import commands
import random
from discord import app_commands

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_balance(self, user_id, amount):
        """Modify balance in memory, mark as modified to avoid excessive saves."""
        user_id = str(user_id)
        self.bot.balances[user_id] = self.bot.balances.get(user_id, 0) + amount
        self.bot.balances_modified = True  # Flag for autosave task

    async def send_balance_embed(self, user, channel):
        """Helper function to send the balance embed (for both slash & prefix commands)."""
        user_id = str(user.id)
        balance = self.bot.balances.get(user_id, 0)
        formatted_balance = f"{balance:,}"

        embed = discord.Embed(
            title="💰 Balance Check",
            description=f"💰 You currently have **{formatted_balance} coins**.",
            color=discord.Color.gold()
        )

        await channel.send(embed=embed)

    # ✅ Slash Command `/balance`
    @app_commands.command(name="balance", description="Check your current balance.")
    async def slash_balance(self, interaction: discord.Interaction):
        print(f"📌 /balance triggered by {interaction.user.name} ({interaction.user.id})")  # Debugging print
        await interaction.response.defer(thinking=True)  # Prevents auto-response issues
        await self.send_balance_embed(interaction.user, interaction.followup)

    # ✅ Prefix Command `!balance`
    @commands.command(name="balance")
    async def prefix_balance(self, ctx):
        await self.send_balance_embed(ctx.author, ctx)

    # ✅ Alias Command `!bal`
    @commands.command(name="bal")
    async def prefix_balance_alias(self, ctx):
        await self.send_balance_embed(ctx.author, ctx)

    @commands.command(name="commands")
    async def command_list(self, ctx):
        """Show available commands."""
        embed = discord.Embed(
            title="📜 Available Commands",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="**🔹 Important Commands**",
            value="`!commands` - Show this help menu",
            inline=False
        )
        embed.add_field(
            name="**💰 Economy Commands**",
            value="`!beg` - Try to get some coins (50% success)\n"
                  "`!bal` - Check your current balance\n"
                  "`!leaderboard` - Show the top richest users",
            inline=False
        )
        embed.add_field(
            name="**🎰 Gamble Commands**",
            value="`!coinflip` - Flip a coin and bet your coins",
            inline=False
        )
        embed.set_footer(text="Use these commands to interact with the economy system!")
        await ctx.send(embed=embed)

    @commands.command()
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
            self.update_balance(ctx.author.id, -loss)

            embed = discord.Embed(
                title="Begging Failed!",
                description=f"{response} {'You lost **' + str(loss) + ' coins**!' if loss > 0 else ''}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        earnings = random.randint(1, 100)
        self.update_balance(ctx.author.id, earnings)

        embed = discord.Embed(
            title="Begging Success!",
            description=f"You begged and received **{earnings} coins**! 🤑",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="lb", aliases=["leaderboard"])
    async def lb(self, ctx):
        """Show the top 10 richest users."""
        sorted_balances = sorted(self.bot.balances.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="Top richest users:",
            color=discord.Color.purple()
        )
        for idx, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"#{idx} {user.name}", value=f"💰 {balance} coins", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
