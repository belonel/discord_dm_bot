import discord
import amplitude_logger
from multiprocessing import Process
from db_helper import *
import json

from boto.s3.connection import S3Connection
import os

# token = S3Connection(os.environ['D_KEY'], os.environ['A_KEY'])
# DISCORD_BOT_TOKEN = token.access_key
# AMPLITUDE_API_KEY = token.secret_key

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True
#
# client = discord.Client(intents=intents)
#
# # initialize amplitude logger
# amplitude_logger = amplitude_logger.AmplitudeLogger(api_key=AMPLITUDE_API_KEY)
#
# @client.event
# async def on_member_update(before, after):
#     if before.status != after.status:
#         roles = []
#         for i in after.roles:
#             roles.append(str(i.name))
#         if len(roles) == 1:
#             role = roles[0]
#         else:
#             role = roles[1]
#
#         print(f'---> before: {before.status}, after: {after.status}, user_after: {after}, role: {role}')
#         event_args = {
#             "user_id": str(after.id),
#             "event_type": "Switched status",
#             "event_properties":
#                 {
#                     "from": str(before.status),
#                     "to": str(after.status),
#                 },
#             "user_properties":
#                 {
#                     "discord_username": str(after.display_name),
#                     "discord_handle": str(after.discriminator),
#                     "joined_discord_at": str(after.joined_at),
#                     "joined_week_number": str(after.joined_at.isocalendar()[1]),
#                     "joined_weekday": str(after.joined_at.isocalendar()[2]),
#                     "discord_roles": role,
#                     "discord_status": str(after.status),
#                 },
#
#         }
#         event = amplitude_logger.create_event(**event_args)
#         # send event to amplitude
#         amplitude_logger.log_event(event)
#
#         if str(before.status) != 'online' and str(after.status) == 'online':
#             # user bacame online
#             print('user bacame online')
#             event_args = {
#                 "user_id": str(after.id),
#                 "event_type": "Switched to online",
#             }
#             event = amplitude_logger.create_event(**event_args)
#             # send event to amplitude
#             amplitude_logger.log_event(event)
#
#         elif str(before.status) != "offline" and str(after.status) == 'offline':
#             # user bacame offline
#             print('user bacame offline')
#             event_args = {
#                 "user_id": str(after.id),
#                 "event_type": "Switched to offline",
#             }
#             event = amplitude_logger.create_event(**event_args)
#             # send event to amplitude
#             amplitude_logger.log_event(event)
#
# @client.event
# async def on_member_join(member):
#     print(f'joined_at: {member.joined_at}\nusername: {member.display_name}\n'
#           f'user_discriminator: {member.discriminator}\nuser_id: {member.id}\n')
#     event_args = {
#         "user_id": str(member.id),
#         "event_type": "Joined discord first time",
#         "user_properties":
#             {
#                 "discord_username": str(member.display_name),
#                 "discord_handle": str(member.discriminator),
#                 "joined_discord_at": str(member.joined_at),
#                 "joined_year": str(member.joined_at.isocalendar()[0]),
#                 "joined_week_number": str(member.joined_at.isocalendar()[1]),
#                 "joined_weekday": str(member.joined_at.isocalendar()[2]),
#                 "discord_roles": "Trial",
#                 "#messages_sent": 0,
#             },
#
#     }
#     event = amplitude_logger.create_event(**event_args)
#     # send event to amplitude
#     amplitude_logger.log_event(event)
#
#     indentify_args = {
#         "user_id": str(member.id),
#         "user_properties": {
#             "$setOnce": {
#                 "joined_discord_at": str(member.joined_at),
#                 "joined_year": str(member.joined_at.isocalendar()[0]),
#                 "joined_week_number": str(member.joined_at.isocalendar()[1]),
#                 "joined_weekday": str(member.joined_at.isocalendar()[2]),
#             }
#         }
#     }
#     identify = amplitude_logger.create_ident(**indentify_args)
#     amplitude_logger.log_ident(identify)
#
#
# @client.event
# async def on_message(message):
#     print(f'Message from {message.author}: {message.content}, channel: {message.channel.name}')
#
#     event_args = {
#         "user_id": str(message.author.id),
#         "event_type": "Message sent",
#         "event_properties": {
#             "channel": str(message.channel.name),
#             "text": str(message.content),
#         },
#         "user_properties":
#             {
#                 "discord_username": str(message.author.display_name),
#                 "discord_handle": str(message.author.discriminator),
#                 "joined_discord_at": str(message.author.joined_at),
#                 "joined_year": str(message.author.joined_at.isocalendar()[0]),
#                 "joined_week_number": str(message.author.joined_at.isocalendar()[1]),
#                 "joined_weekday": str(message.author.joined_at.isocalendar()[2]),
#             },
#
#     }
#     event = amplitude_logger.create_event(**event_args)
#     # send event to amplitude
#     amplitude_logger.log_event(event)
#
#     indentify_args = {
#         "user_id": str(message.author.id),
#         "user_properties": {
#             "$add": {"#messages_sent": 1}
#         }
#     }
#     identify = amplitude_logger.create_ident(**indentify_args)
#     amplitude_logger.log_ident(identify)
#
# @client.event
# async def on_reaction_add(reaction, user):
#     emoji = reaction.emoji
#     print(f'reaction: {emoji}, message: {reaction.message.content}, user: {user.display_name}, author: {reaction.message.author.display_name}')
#
#     if '<:' in str(emoji):
#         emoji = str(emoji)
#
#     event_args = {
#         "user_id": str(user.id),
#         "event_type": "Reaction added",
#         "event_properties": {
#             "emoji": emoji,
#             "channel": str(reaction.message.channel.name),
#             "message_text": str(reaction.message.content),
#             "message_author": str(reaction.message.author.display_name)
#         },
#         "user_properties":
#             {
#                 "discord_username": str(user.display_name),
#                 "discord_handle": str(user.discriminator),
#                 "joined_discord_at": str(user.joined_at),
#                 "joined_year": str(user.joined_at.isocalendar()[0]),
#                 "joined_week_number": str(user.joined_at.isocalendar()[1]),
#                 "joined_weekday": str(user.joined_at.isocalendar()[2]),
#             },
#     }
#     event = amplitude_logger.create_event(**event_args)
#     # send event to amplitude
#     amplitude_logger.log_event(event)
#
# def bot_run():
#     client.run(DISCORD_BOT_TOKEN)
#
# def server_run():
#     if len(argv) == 2:
#         run(port=int(argv[1]))
#     else:
#         run()
#
# if __name__ == "__main__":
#     Process(target=server_run).start()
#     Process(target=bot_run).start()
#


from flask import Flask, request, abort, jsonify
app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_push():
    if not request.json:
        abort(400)
    print("Request dictionary: {}".format(request.json))

    data = json.loads(request.decode('utf-8'))
    if data['email'] != None and data['stripe_cust_id'] != None \
            and data['created_at'] != None and data['invite_code'] != None:
        save_email(data['email'], data['stripe_cust_id'], data['invite_code'], data['created_at'])
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("Listening...")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
