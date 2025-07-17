import discord
from discord.ext import commands, tasks
from discord.ui import View, Select, Button
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1394312686090715248
JOIN_ROLE_ID = 1395166044762542222  # FREE Role

premium_role_id = 1395166045974560829
free_role_id = 1395166044762542222

CATEGORY_IDS = {
    "BuyCoins": None,
    "BugReports": None,
    "General": None,
    "Partnership": None
}

channel_auto_posts = {
    1395166052127871066: "# 🎉 Earn Premium Access – Invite Reward System!\n\nWant access to exclusive premium channels? Just invite your friends! 💎\n\n👉 **As soon as you hit 5 invites**, you’ll automatically unlock:\n• **💰 <#1395166058620387378>**\n• **🛸 <#1395166059463573526>**\n•** 🎯 <#1395166061313265709>**\n•** 📊 <#1395166064471445635>**\n\n**Use !invites** to check your progress and enjoy premium benefits! 🚀",
    1395166053159407687: "# 🎉 Earn Premium Access – Invite Reward System!\n\nWant access to exclusive premium channels? Just invite your friends! 💎\n\n👉 **As soon as you hit 5 invites**, you’ll automatically unlock:\n• **💰 <#1395166058620387378>**\n• **🛸 <#1395166059463573526>**\n•** 🎯 <#1395166061313265709>**\n•** 📊 <#1395166064471445635>**\n\n**Use !invites** to check your progress and enjoy premium benefits! 🚀"
}

counter = 1

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)

    # Rollen-Zuweisung bei Join
    @bot.event
    async def on_member_join(member):
        role = member.guild.get_role(JOIN_ROLE_ID)
        await member.add_roles(role)

    # Kategorien erstellen, falls nicht vorhanden
    for name in CATEGORY_IDS:
        if not any(c.name == name for c in guild.categories):
            cat = await guild.create_category(name)
            CATEGORY_IDS[name] = cat.id
        else:
            CATEGORY_IDS[name] = discord.utils.get(guild.categories, name=name).id

    # Dropdown direkt posten
    channel = discord.utils.get(guild.text_channels, name="ticket-support")
    if channel:
        await send_dropdown(channel)

    post_auto_message.start()

# Dropdown-UI
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="BuyCoins", description="Purchase-related help"),
            discord.SelectOption(label="BugReports", description="Report a bug"),
            discord.SelectOption(label="General", description="General questions"),
            discord.SelectOption(label="Partnership", description="Partnership inquiries"),
        ]
        super().__init__(placeholder="📩 Create a Ticket", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        global counter
        choice = self.values[0]
        guild = interaction.guild
        cat_id = CATEGORY_IDS.get(choice)
        category = discord.utils.get(guild.categories, id=cat_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            discord.utils.get(guild.roles, id=premium_role_id): discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, id=free_role_id): discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{counter:03d}",
            category=category,
            overwrites=overwrites
        )
        counter += 1

        msg = f"Hello {interaction.user.mention}, thank you for creating a **{choice}** ticket.\nPlease describe your issue clearly."

        if choice == "BuyCoins":
            msg += "\n\nPlease also include:\n- Your Username\n- Platform (PS/Xbox/PC)\n- Coin Amount\n- Backup Codes"

        await ticket_channel.send(msg)
        await ticket_channel.send("🔒 Use `/close` or click below to close the ticket.", view=CloseButton())

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket"))

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

async def send_dropdown(channel):
    await channel.purge()
    await channel.send("📩 **Select a category to create a ticket:**", view=TicketView())

# Auto-Post in bestimmten Channels
@tasks.loop(hours=3)
async def post_auto_message():
    for channel_id, message in channel_auto_posts.items():
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
