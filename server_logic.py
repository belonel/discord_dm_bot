from config import *
import psycopg2
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
