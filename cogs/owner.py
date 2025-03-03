import discord
import time
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # Track bot uptime
        self.owners = {bot.owner_id, 788507999748227073}  # Ensure your ID is included

    async def is_additional_owner(self, ctx):
        return ctx.author.id in self.owners

    @commands.command()
    @commands.is_owner()
    async def addowner(self, ctx, member: discord.Member):
        """Grants owner permissions to a user"""
        self.owners.add(member.id)
        await ctx.send(f"✅ {member.mention} has been granted owner permissions!")

    @commands.command()
    @commands.is_owner()
    async def removeowner(self, ctx, member: discord.Member):
        """Revokes owner permissions from a user"""
        if member.id in self.owners:
            self.owners.remove(member.id)
            await ctx.send(f"❌ {member.mention} no longer has owner permissions.")
        else:
            await ctx.send(f"⚠ {member.mention} is not an owner.")

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        """Gives money to a user (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        user_id = str(member.id)
        # Ensure the balance structure exists, initialize if not
        if user_id not in self.bot.balances or not isinstance(self.bot.balances[user_id], dict):
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}

        self.bot.balances[user_id]["cash"] += amount  # Add to the cash balance
        self.bot.balances_modified = True

        embed = discord.Embed(
            title="Balance Updated!",
            description=f"Added **{amount} coins** to {member.mention}'s cash balance.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def resetbal(self, ctx, member: discord.Member):
        """Resets a user's balance (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        user_id = str(member.id)
        # Ensure the balance structure exists, initialize if not
        if user_id not in self.bot.balances or not isinstance(self.bot.balances[user_id], dict):
            self.bot.balances[user_id] = {"cash": 0, "bank": 0}

        self.bot.balances[user_id] = {"cash": 0, "bank": 0}  # Reset both cash and bank
        self.bot.balances_modified = True

        embed = discord.Embed(
            title="Balance Reset!",
            description=f"{member.mention}'s balance has been reset to **0 coins** in both cash and bank.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def announce(self, ctx, *, message: str):
        """Broadcasts a message (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.gold()
        )
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed)
                    break
        await ctx.send("Announcement sent!")

    @commands.command()
    async def shutdown(self, ctx):
        """Safely shuts down the bot (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        await ctx.send("Shutting down... 🛑")
        await self.bot.close()

    @commands.command()
    async def reloadcog(self, ctx, cog: str):
        """Reloads a cog dynamically (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        try:
            await self.bot.reload_extension(f'cogs.{cog}')
            await ctx.send(f"🔄 Reloaded `{cog}` successfully!")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog}`: {e}")

    @commands.command()
    async def botstats(self, ctx):
        """Shows bot statistics (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        uptime = round(time.time() - self.start_time)
        total_users = sum(len(guild.members) for guild in self.bot.guilds)
        embed = discord.Embed(
            title="📊 Bot Stats",
            color=discord.Color.purple()
        )
        embed.add_field(name="Uptime", value=f"{uptime} seconds", inline=False)
        embed.add_field(name="Total Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Total Users", value=f"{total_users}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def setprefix(self, ctx, new_prefix: str):
        """Changes the bot's command prefix (Owner Only)"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        self.bot.command_prefix = new_prefix
        await ctx.send(f"✅ Prefix changed to `{new_prefix}`")

    @commands.command(name="oc")
    async def owner_commands(self, ctx):
        """Lists all owner-only commands"""
        if not await self.is_additional_owner(ctx):
            return await ctx.send("⛔ You are not an owner!")

        embed = discord.Embed(
            title="🛠️ Owner Commands",
            description="Here are the commands only the bot owner can use:",
            color=discord.Color.orange()
        )
        embed.add_field(name="💰 Economy Management", value="`!give`, `!resetbal`, `!setbal`, `!savebalances`", inline=False)
        embed.add_field(name="⚙️ Bot Management", value="`!shutdown`, `!reloadcog`, `!setprefix`, `!addowner`, `!removeowner`", inline=False)
        embed.add_field(name="📢 Announcements", value="`!announce`", inline=False)
        embed.add_field(name="📊 Stats", value="`!botstats`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def checkowner(self, ctx):
        """Check if you're recognized as an owner"""
        await ctx.send(f"Your ID: {ctx.author.id}")
        await ctx.send(f"Owners: {self.owners}")
        if await self.is_additional_owner(ctx):
            await ctx.send("✅ You ARE an owner!")
        else:
            await ctx.send("⛔ You are NOT an owner!")


async def setup(bot):
    await bot.add_cog(Owner(bot))
