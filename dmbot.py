from discord.ext import commands
import discord
import os

from boto.s3.connection import S3Connection
# token = S3Connection(os.environ['D'])


bot = commands.Bot(command_prefix='!')

@bot.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "This Message is sent via DM"
    await user.send(message)

bot.run('token')
