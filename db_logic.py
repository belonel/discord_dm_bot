import psycopg2
from config import *


def insert_user(email, stripe_id, created_at, invite_code, server_name, product_name):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        cur.execute(f"INSERT INTO users(email, stripe_cust_id, created_at, invite_code, discord_server_name, plan_name) values('{email}', '{stripe_id}', '{created_at}', '{invite_code}', '{server_name}', '{product_name}');")
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


def get_all_users():
    conn = None
    result = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        cur.execute('SELECT * FROM USERS;')

        result = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            return result
            # print('Database connection closed.')

def get_user_by_invite_code(inv_code):
    conn = None
    result = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        print('script result:')
        cur.execute('SELECT * from users where;')

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

def get_user_by_discord_id():
    pass

def update_by_invite_code_and_server_name(invite_code, username, user_id, joined_at, server_name):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        # execute a statement
        if 'Super' in server_name:
            cur.execute(
                f"UPDATE users SET discord_username = '{username}' where invite_code='{invite_code}' and discord_server_name = 'Super Forecasters'; "
                f"UPDATE users SET discord_id = '{user_id}' where invite_code='{invite_code}' and discord_server_name = 'Super Forecasters'; "
                f"UPDATE users SET joined_at = '{joined_at}' where invite_code='{invite_code}' and discord_server_name = 'Super Forecasters'; ")
        elif 'Macro' in server_name:
            cur.execute(f"UPDATE users SET discord_username = '{username}' where invite_code='{invite_code}' and discord_server_name = 'Macro Sentiments'; "
                        f"UPDATE users SET discord_id = '{user_id}' where invite_code='{invite_code}' and discord_server_name = 'Macro Sentiments'; "
                        f"UPDATE users SET joined_at = '{joined_at}' where invite_code='{invite_code}' and discord_server_name = 'Macro Sentiments'; ")

        conn.commit()
        print('data updated')
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def get_email_by_discord_id(discord_user_id):
    conn = None
    result = None

    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()

        # execute a statement
        print('discord user email: ')
        cur.execute(f"SELECT email from users where discord_id = '{discord_user_id}';")

        result = cur.fetchall()[0][0]

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            return result
            # print('Database connection closed.')
