import discord
from config import *
from db_logic import *

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)

invites = {}

users = []

def get_email_from_local_by_discord_id(discord_id):
    global users
    found = False
    for user in users:
        if user[6] == str(discord_id):
            found = True
            return user[1]
    if not found:
        #загрузи, обнови users, повтори поиск
        users = get_all_users()
    for user in users:
        if user[6] == str(discord_id):
            found = True
            return user[1]
    if found == False:
        # print(f"user_id: {discord_id}")
        # print('all users now: ', users)
        return None

@client.event
async def on_ready():
    print('Bot ready\n')
    # Getting all the guilds our bot is in
    for guild in client.guilds:
        # Adding each guild's invites to our dict
        invites[guild.id] = await guild.invites()
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
    invites[invite.guild.id] = current_invites


@client.event
async def on_member_join(member):
    print(f'User joined!! at: {member.joined_at}, username: {member.display_name}\n'
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

    update_by_invite_code(used_invite.code, member.name, member.id, member.joined_at)

    user_email = ''
    user_id_to_amplitude = ''


    if used_invite.max_uses == 1:
        user_email = get_email_from_local_by_discord_id(member.id)
        print(f'joined user email: {user_email}')
        if user_email != None:
            # отправляем ивент с user_id = email
            user_id_to_amplitude = user_email
    else:
        # отправляем ивент с user_id = discord_id
        user_id_to_amplitude = member.id

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
    if before.status != after.status:
        roles = []
        for i in after.roles:
            roles.append(str(i.name))
        if len(roles) == 1:
            role = roles[0]
        else:
            role = roles[1]

        # print(f'---> before: {before.status}, after: {after.status}, user_after: {after}, role: {role}')

        user_email = get_email_from_local_by_discord_id(after.id)
        user_id_to_amplitude = ''

        if user_email != None:
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

        if str(before.status) != 'online' and str(after.status) == 'online':
            # user bacame online
            # print('user bacame online\n')
            event_args = {
                "user_id": str(user_id_to_amplitude),
                "event_type": "Switched to online",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)

        elif str(before.status) != "offline" and str(after.status) == 'offline':
            # user bacame offline
            # print('user bacame offline\n')
            event_args = {
                "user_id": str(user_id_to_amplitude),
                "event_type": "Switched to offline",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)
        elif str(before.status) != "idle" and str(after.status) == 'idle':
            # user bacame idle
            # print('user bacame idle\n')
            event_args = {
                "user_id": str(user_id_to_amplitude),
                "event_type": "Switched to idle",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)
        elif str(before.status) != "dnd" and str(after.status) == 'dnd':
            # user bacame dnd
            # print('user became dont disturb\n')
            event_args = {
                "user_id": str(user_id_to_amplitude),
                "event_type": "Switched to dnd",
            }
            event = amplitude_logger.create_event(**event_args)
            # send event to amplitude
            amplitude_logger.log_event(event)


@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}, channel: {message.channel.name}')
    # print(f'channels: \n {message.guild.channels}')
    # if message.content == 'create_new_invite' and message.channel.name == 'test-bot-integration':
    #     for server in client.guilds:
    #         if server.name == "Cindicator's Macro Sentiment":
    #             for channel in server.channels:
    #                 if channel.name == "newcomers-questions":
    #                     invite = await channel.create_invite(max_uses=1, unique=True)
    #                     print(f'invite to {channel} created')
    #                     print(f'link: {invite}')
    #                     await message.channel.send("Created")

    user_email = get_email_from_local_by_discord_id(message.author.id)
    user_id_to_amplitude = ''

    if user_email != None:
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
    print(f'reaction: {emoji}, message: {reaction.message.content}, user: {user.display_name}, author: {reaction.message.author.display_name}')

    if '<:' in str(emoji):
        emoji = str(emoji)

    user_email = get_email_from_local_by_discord_id(user.id)
    user_id_to_amplitude = ''

    if user_email != None:
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

async def create_invite():
    print('create invite function')
    print('client: ', client)
    print('guilds: ', client.guilds)
    print('chennels: ', client.guilds[0].channels)
    print('chennels: ', client.guilds[0].channels[0])
    for server in client.guilds:
        print('guilds cycle')
        if server.name == "Cindicator's Macro Sentiment":
            for channel in server.channels:
                print('channels cycle')
                if channel.name == "newcomers-questions":
                    invite = await channel.create_invite(max_uses=1, unique=True)
                    print(f'invite to {channel} created')
                    print(f'link: {invite}')
                    return invite
    return "nothing happened"
