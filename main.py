import discord
import asyncio
import json
import praw

# Load config
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["discord_token"]
CHANNEL_ID = int(config["channel_id"])

# Set up Reddit API (using public access)
reddit = praw.Reddit(
    client_id="dummy",
    client_secret="dummy",
    user_agent="freestuff-bot"
)

# Set up Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Keep track of seen posts
seen = set()

async def fetch_and_post():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found!")
        return

    subreddit = reddit.subreddit("FreeGameFindings")
    async for submission in async_iter_subreddit(subreddit, limit=10):
        if submission.id not in seen:
            seen.add(submission.id)
            await channel.send(f"🎮 **{submission.title}**\n{submission.url}")

async def async_iter_subreddit(subreddit, limit=10):
    # Make PRAW subreddit iterable with asyncio
    loop = asyncio.get_event_loop()
    posts = await loop.run_in_executor(None, lambda: list(subreddit.new(limit=limit)))
    for post in posts:
        yield post

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    while True:
        await fetch_and_post()
        await asyncio.sleep(1800)  # 30 minutes

client.run(TOKEN)
