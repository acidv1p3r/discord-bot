import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
import os

# Load patchnotes
with open("patchnotes.json") as f:
    PATCH_NOTES = json.load(f)

# Load or initialize settings
SETTINGS_FILE = "settings.json"
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
else:
    settings = {}

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# Set up Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")
    auto_post.start()

# Commands
@bot.tree.command(name="help", description="Show help message")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**FreeStuffBot Commands:**\n"
        "`/help` - Show this message\n"
        "`/free` - Post latest free game deals\n"
        "`/settings` - Configure bot for this server\n"
        "`/invite` - Get the bot invite link\n"
        "`/about` - Info about the bot\n"
        "`/patchnotes` - View latest patch notes",
        ephemeral=True
    )

@bot.tree.command(name="free", description="Get latest free game deals")
async def free_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send("🎮 **Free Game:** https://www.reddit.com/r/FreeGameFindings/")

@bot.tree.command(name="invite", description="Bot invite link")
async def invite_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("🔗 Invite me with: https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands")

@bot.tree.command(name="about", description="About the bot")
async def about_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 FreeStuffBot — Get the latest free games every 30 mins!
Made with ❤️")

@bot.tree.command(name="patchnotes", description="Latest bot updates")
async def patchnotes_cmd(interaction: discord.Interaction):
    notes = "\n".join(f"**v{v}**: {msg}" for v, msg in PATCH_NOTES.items())
    await interaction.response.send_message(f"📜 **Patch Notes**:\n{notes}")

@bot.tree.command(name="settings", description="Configure bot for this server")
@app_commands.describe(channel="Channel to post free game alerts")
async def settings_cmd(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    settings[guild_id] = {
        "channel_id": channel.id,
        "autopost": True
    }
    save_settings()
    await interaction.response.send_message(f"✅ Bot configured to post in {channel.mention}", ephemeral=True)

# Task: Auto post every 30 minutes
@tasks.loop(minutes=30)
async def auto_post():
    for guild_id, cfg in settings.items():
        if cfg.get("autopost"):
            try:
                channel = bot.get_channel(cfg["channel_id"])
                if channel:
                    await channel.send("🎮 **Free Game Alert!** https://www.reddit.com/r/FreeGameFindings/")
            except Exception as e:
                print(f"[AutoPost Error] {e}")

# Load token
with open("config.json") as f:
    TOKEN = json.load(f)["discord_token"]

bot.run(TOKEN)
