from config import *
from db_logic import *
from flask import Flask, request, abort, jsonify
from datetime import date
from datetime import datetime

from bot_logic import *
import asyncio

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_push():
    print(request.data.decode('utf-8'))
    if not request.json:
        abort(400)
    print("Request dictionary: {}".format(request.json))

    data = request.json
    if data['email'] != None and data['stripe_cust_id'] != None \
            and data['created_at'] != None and data['invite_code'] != None \
            and data['product_name'] != None and data['subs_price'] != None and data['subs_interval'] != None:
        insert_user(data['email'], data['stripe_cust_id'], data['created_at'], data['invite_code'])
        event_args = {
            "user_id": str(data['email']),
            "event_type": "Trial started",
            "event_properties": {
                "product_name": data['product_name'],
                "subscription_price": data['subs_price'],
                "subscription_interval": data['subs_interval'],
            },
            "user_properties": {
                "discord_invite_code": data['invite_code'],
            }
        }
        event = amplitude_logger.create_event(**event_args)
        # send event to amplitude
        amplitude_logger.log_event(event)

        indentify_args = {
            "user_id": str(data['email']),
            "user_properties": {
                "$setOnce": {
                    "cohort_day_number": datetime.now().timetuple().tm_yday,
                    "cohort_week_number": date.today().isocalendar()[1],
                    "cohort_month": datetime.now().timetuple().tm_mon,
                    "cohort_year": datetime.now().timetuple().tm_year,
                    "trial_started_at": datetime.now().isoformat(),
                },
            }
        }
        identify = amplitude_logger.create_ident(**indentify_args)
        amplitude_logger.log_ident(identify)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    new_invite = None
    done = loop.run_until_complete(create_invite())
    print(done)
    new_invite = str(done)
    loop.close()


    return jsonify({'status': 'ok', 'invite_link': new_invite}), 200
