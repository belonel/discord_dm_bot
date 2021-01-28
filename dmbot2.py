import discord
import amplitude_logger
from multiprocessing import Process
from db_helper import *
import json
import psycopg2

# DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL = "postgres://anjyujjlcqgupd:f4776575e1d67ac5f10612f2af981c55464e6b6a9348f7c8c01666cd73548aa9@ec2-50-19-247-157.compute-1.amazonaws.com:5432/dakhb74dv1ma6f"

from boto.s3.connection import S3Connection
import os

token = S3Connection(os.environ['D_KEY'], os.environ['A_KEY'])
DISCORD_BOT_TOKEN = token.access_key
AMPLITUDE_API_KEY = token.secret_key

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)

# initialize amplitude logger
amplitude_logger = amplitude_logger.AmplitudeLogger(api_key=AMPLITUDE_API_KEY)

@client.event
async def on_member_update(before, after):
    if before.status != after.status:
        roles = []
        for i in after.roles:
            roles.append(str(i.name))
        if len(roles) == 1:
            role = roles[0]
        else:
            role = roles[1]

        print(f'---> before: {before.status}, after: {after.status}, user_after: {after}, role: {role}')
        event_args = {
            "user_id": str(after.id),
            "event_type": "Switched status",
            "event_properties":
                {
                    "from": str(before.status),
                    "to": str(after.status),
                },
            "user_properties":
                {
                    "discord_username": str(after.display_name),
                    "discord_handle": str(after.discriminator),
                    "joined_discord_at": str(after.joined_at),
                    "joined_week_number": str(after.joined_at.isocalendar()[1]),
                    "joined_weekday": str(after.joined_at.isocalendar()[2]),
                    "discord_roles": role,
                    "discord_status": str(after.status),
                },

        }
        event = amplitude_logger.create_event(**event_args)
        # send event to amplitude
        amplitude_logger.log_event(event)

        if str(before.status) != 'online' and str(after.status) == 'online':
            # user bacame online
            print('user bacame online')
            event_args = {
                "user_id": str(after.id),
                "event_type": "Switched to online",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)

        elif str(before.status) != "offline" and str(after.status) == 'offline':
            # user bacame offline
            print('user bacame offline')
            event_args = {
                "user_id": str(after.id),
                "event_type": "Switched to offline",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)

@client.event
async def on_member_join(member):
    print(f'joined_at: {member.joined_at}\nusername: {member.display_name}\n'
          f'user_discriminator: {member.discriminator}\nuser_id: {member.id}\n')
    event_args = {
        "user_id": str(member.id),
        "event_type": "Joined discord first time",
        "user_properties":
            {
                "discord_username": str(member.display_name),
                "discord_handle": str(member.discriminator),
                "joined_discord_at": str(member.joined_at),
                "joined_year": str(member.joined_at.isocalendar()[0]),
                "joined_week_number": str(member.joined_at.isocalendar()[1]),
                "joined_weekday": str(member.joined_at.isocalendar()[2]),
                "discord_roles": "Trial",
                "#messages_sent": 0,
            },

    }
    event = amplitude_logger.create_event(**event_args)
    # send event to amplitude
    amplitude_logger.log_event(event)

    indentify_args = {
        "user_id": str(member.id),
        "user_properties": {
            "$setOnce": {
                "joined_discord_at": str(member.joined_at),
                "joined_year": str(member.joined_at.isocalendar()[0]),
                "joined_week_number": str(member.joined_at.isocalendar()[1]),
                "joined_weekday": str(member.joined_at.isocalendar()[2]),
            }
        }
    }
    identify = amplitude_logger.create_ident(**indentify_args)
    amplitude_logger.log_ident(identify)


@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}, channel: {message.channel.name}')

    event_args = {
        "user_id": str(message.author.id),
        "event_type": "Message sent",
        "event_properties": {
            "channel": str(message.channel.name),
            "text": str(message.content),
        },
        "user_properties":
            {
                "discord_username": str(message.author.display_name),
                "discord_handle": str(message.author.discriminator),
                "joined_discord_at": str(message.author.joined_at),
                "joined_year": str(message.author.joined_at.isocalendar()[0]),
                "joined_week_number": str(message.author.joined_at.isocalendar()[1]),
                "joined_weekday": str(message.author.joined_at.isocalendar()[2]),
            },

    }
    event = amplitude_logger.create_event(**event_args)
    # send event to amplitude
    amplitude_logger.log_event(event)

    indentify_args = {
        "user_id": str(message.author.id),
        "user_properties": {
            "$add": {"#messages_sent": 1}
        }
    }
    identify = amplitude_logger.create_ident(**indentify_args)
    amplitude_logger.log_ident(identify)

@client.event
async def on_reaction_add(reaction, user):
    emoji = reaction.emoji
    print(f'reaction: {emoji}, message: {reaction.message.content}, user: {user.display_name}, author: {reaction.message.author.display_name}')

    if '<:' in str(emoji):
        emoji = str(emoji)

    event_args = {
        "user_id": str(user.id),
        "event_type": "Reaction added",
        "event_properties": {
            "emoji": emoji,
            "channel": str(reaction.message.channel.name),
            "message_text": str(reaction.message.content),
            "message_author": str(reaction.message.author.display_name)
        },
        "user_properties":
            {
                "discord_username": str(user.display_name),
                "discord_handle": str(user.discriminator),
                "joined_discord_at": str(user.joined_at),
                "joined_year": str(user.joined_at.isocalendar()[0]),
                "joined_week_number": str(user.joined_at.isocalendar()[1]),
                "joined_weekday": str(user.joined_at.isocalendar()[2]),
            },
    }
    event = amplitude_logger.create_event(**event_args)
    # send event to amplitude
    amplitude_logger.log_event(event)

def bot_run():
    client.run(DISCORD_BOT_TOKEN)

def server_run():
    print("Listening...")
    # app.run(debug=True, host='0.0.0.0', port=8085)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, abort, jsonify
app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_push():
    print(request.data.decode('utf-8'))
    if not request.json:
        abort(400)
    print("Request dictionary: {}".format(request.json))

    data = request.json
    if data['email'] != None and data['stripe_cust_id'] != None \
            and data['created_at'] != None and data['invite_code'] != None:
        insert_user(data['email'], data['stripe_cust_id'], data['created_at'], data['invite_code'])
    return jsonify({'status': 'ok'}), 200


def insert_user(email, stripe_id, created_at, invite_code):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        cur.execute(f"INSERT INTO users(email, stripe_cust_id, created_at, invite_code) values('{email}', '{stripe_id}', '{created_at}', '{invite_code}');")

        conn.commit()
        print('data inserted')
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def print_all_users():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        print('script result:')
        cur.execute('SELECT * FROM USERS;')

        result = cur.fetchall()
        print(result)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')

if __name__ == '__main__':
    # print_all_users()

    Process(target=server_run).start()
    Process(target=bot_run).start()
