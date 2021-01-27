from tinydb import TinyDB, Query

db = TinyDB('db.json')

def save_email (email, stipe_cust_id, invite_code, created_at):
    db.insert({
        'user_email': email,
        'stripe_cust_id': stipe_cust_id,
        'invite_code': invite_code,
        'discord_username': None,
        'discord_id': None,
        'created_at': created_at,
        'joined_at': None,
    })
    print('=> Trial User Data Inserted')

def save_discord_username (invite_code, discord_username, discord_id, joined_at):
    User = Query()
    db.update({'discord_username': discord_username}, User.invite_code == invite_code)
    db.update({'discord_id': discord_id}, User.invite_code == invite_code)
    db.update({'joined_at': joined_at}, User.invite_code == invite_code)
    print('=> User Data Updated')

# TEST
# save_email('ksandr.lr@gmail.com', 'cus_kjhgfdhjk8765', 'dkfj348', '25-01-2021')
# save_discord_username('dkfj348', 'alex_lider', 'id32454', '26-01-2021')