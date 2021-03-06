import requests
import discord
from config import *
from db_logic import *
from stripe_logic import *

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)

invites = {}

users = []

def get_user_data_from_local_by_discord_id_and_guild_name_and_invite_code(discord_id, guild_name, invite_code = None, subs_name = None):
    global users
    found = False
    my_server_name = ''
    if 'Macro' in guild_name:
        my_server_name = 'Macro Sentiments'
    elif 'Super' in guild_name:
        my_server_name = 'Super Forecasters'

    for user in users:
        if user[6] == str(discord_id) and user[8] == str(my_server_name) and invite_code != None and user[4] == str(invite_code):
            found = True
            return user
    if not found:
        #загрузи, обнови users, повтори поиск
        users = get_all_users()
    for user in users:
        if user[6] == str(discord_id) and user[8] == str(my_server_name):
            found = True
            return user
    if found == False:
        # print(f"user_id: {discord_id}")
        # print('all users now: ', users)
        return None

@client.event
async def on_ready():
    await client.wait_until_ready()
    print(f'Bot ready on guilds: {client.guilds}\n')
    # Getting all the guilds our bot is in
    for guild in client.guilds:
        # Adding each guild's invites to our dict
        try:
            invites[guild.id] = await guild.invites()
        except Exception as e:
            print(e, '\n', guild)
    users = get_all_users()
    print(users)

def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv


@client.event
async def on_invite_create(invite):
    global invites
    current_invites = await invite.guild.invites()
    print("new invite: ", invite)
    print("max uses: ", invite.max_uses)
    print("server name: ", invite.guild.name)
    invites[invite.guild.id] = current_invites


@client.event
async def on_member_join(member):
    print(f'User joined to {member.guild.name}!! at: {member.joined_at}, username: {member.display_name}\n'
          f'user_discriminator: {member.discriminator}, user_id: {member.id}\n')

    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()

    invite_is_temp = False
    used_invite = None

    for invite in invites_before_join:
        if invite not in invites_after_join:
            invite_is_temp = True
            used_invite = invite
            print(f"Member {member.name} Joined")
            print(f"Invite Code: {invite.code}")
            print(f"Inviter: {invite.inviter}\n")

            invites[member.guild.id] = invites_after_join
            break

    if not invite_is_temp:
        for invite in invites_before_join:
            if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
                used_invite = invite
                print(f"Member {member.name} Joined")
                print(f"Invite Code: {invite.code}")
                print(f"Inviter: {invite.inviter}\n")

                invites[member.guild.id] = invites_after_join
                break

    update_by_invite_code_and_server_name(used_invite.code, member.name, member.id, member.joined_at, member.guild.name)

    user_email = ''
    user_id_to_amplitude = ''


    if used_invite.inviter.name == 'Integromat':
        print(f'inviter name: {used_invite.inviter.name}')

        user_data = get_user_data_from_local_by_discord_id_and_guild_name_and_invite_code(member.id, member.guild.name, used_invite.code)
        user_email = user_data[1] if (user_data != None) else None
        user_stripe_id = user_data[2] if (user_data != None) else None

        print(f'joined user email: {user_email}')
        if user_data != None:
            # отправляем ивент с user_id = email
            user_id_to_amplitude = user_email
            #добавляем в карточку кастомера в страйпе ник
            update_customer_description(user_stripe_id, member.display_name + '#' + member.discriminator)
            update_customer_metadata(user_stripe_id, {"discord_nickname": member.display_name,
                                                      "discord_user_id": member.id})
            #отправляем запрос в запиер, чтобы добавить в табличку и дать роль
            #если продукт юзера - комьюнити
            if 'Community' in user_data[9]:
                print("this is community member")
                url = 'https://hooks.zapier.com/hooks/catch/8089142/byi75p1/'
                body = {
                    "event_name": "joined_discord",
                    "email": str(user_data[1]),
                    "stripe_cust_id": str(user_data[2]),
                    "created_at": str(user_data[3]),
                    "invite_code": str(user_data[4]),
                    "joined_at": str(member.joined_at),
                    "discord_nickname": member.display_name + '#' + member.discriminator,
                    "discord_id": str(member.id)
                }
                x = requests.post(url, json=body)

    else:
        # отправляем ивент с user_id = discord_id
        user_id_to_amplitude = member.id

    if 'Macro' in member.guild.name:
        event_args = {
            "user_id": str(user_id_to_amplitude),
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
            "user_id": str(user_id_to_amplitude),
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
async def on_member_update(before, after):
    if 'Macro' in before.guild.name:
        if before.status != after.status:
            roles = []
            for i in after.roles:
                roles.append(str(i.name))
            if len(roles) == 1:
                role = roles[0]
            else:
                role = roles[1]

            # print(f'---> before: {before.status}, after: {after.status}, user_after: {after}, role: {role}')

            user_data = get_user_data_from_local_by_discord_id_and_guild_name_and_invite_code(after.id, after.guild.name)
            user_email = user_data[1] if (user_data != None) else None
            user_id_to_amplitude = ''

            if user_data != None:
                user_id_to_amplitude = user_email
            else:
                # print(f"-?-> I don't know email for user @{after.display_name} in discord")
                user_id_to_amplitude = after.id

            event_args = {
                "user_id": str(user_id_to_amplitude),
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

@client.event
async def on_message(message):
    print(f'server: {message.author.guild.name}, \n'
          f'Message from {message.author}: {message.content}, channel: {message.channel.name}')
    if 'Macro' in message.author.guild.name:

        if message.channel.name == 'test-bot-integration' or message.channel.name == 'moderator-only' or message.channel.name == 'moderator-only-test':
            return

        user_data = get_user_data_from_local_by_discord_id_and_guild_name_and_invite_code(message.author.id, message.author.guild.name)
        user_email = user_data[1] if (user_data != None) else None
        user_id_to_amplitude = ''

        for role in message.author.roles:
            if 'Community' in role.name and 'Trial' in role.name: 
                print("message from community subscriber")
                url = 'https://hooks.zapier.com/hooks/catch/8089142/byi75p1/'
                body = {
                    "event_name": "message",
                    "discord_nickname": message.author.display_name + '#' + message.author.discriminator,
                    "discord_id": str(message.author.id),
                    "message_text": str(message.content)
                }
                x = requests.post(url, json=body)

        if user_data != None:
            user_id_to_amplitude = user_email

        else:
            print(f"-?-> I don't know email for user {message.author.display_name} in discord\n")
            user_id_to_amplitude = message.author.id

        event_args = {
            "user_id": str(user_id_to_amplitude),
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
            "user_id": str(user_id_to_amplitude),
            "user_properties": {
                "$add": {"#messages_sent": 1}
            }
        }
        identify = amplitude_logger.create_ident(**indentify_args)
        amplitude_logger.log_ident(identify)

@client.event
async def on_reaction_add(reaction, user):
    emoji = reaction.emoji
    print(
        f'server: {reaction.user.guild.name}, \n'
        f'reaction: {emoji}, message: {reaction.message.content}, user: {user.display_name}, author: {reaction.message.author.display_name}')

    if 'Macro' in user.guild.name:

        if '<:' in str(emoji):
            emoji = str(emoji)

        user_data = get_user_data_from_local_by_discord_id_and_guild_name_and_invite_code(user.id, user.guild.name)
        user_email = user_data[1] if (user_data != None) else None

        user_id_to_amplitude = ''

        if user_data != None:
            user_id_to_amplitude = user_email
        else:
            print(f"-?-> I don't know email for user {user.display_name} in discord\n")
            user_id_to_amplitude = user.id

        event_args = {
            "user_id": str(user_id_to_amplitude),
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
