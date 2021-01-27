from discord.ext import commands
import discord
from boto.s3.connection import S3Connection
import os

token = S3Connection(os.environ['D_KEY'], os.environ['A_KEY'])
DISCORD_BOT_TOKEN = token.access_key

bot = commands.Bot(command_prefix='!')

@bot.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "This Message is sent via DM"
    await user.send(message)

bot.run(DISCORD_BOT_TOKEN)
