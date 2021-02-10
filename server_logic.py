from config import *
from db_logic import *
from flask import Flask, request, abort, jsonify
from datetime import date
from datetime import datetime

from bot_logic import *
import asyncio

app = Flask(__name__)

@app.route('/trial', methods=['POST'])
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
                "stripe_cust_id": data['stripe_cust_id'],
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
                "$append": {
                    "subscribed_to": data['product_name']
                }
            }
        }
        identify = amplitude_logger.create_ident(**indentify_args)
        amplitude_logger.log_ident(identify)

    return jsonify({'status': 'ok'}), 200


@app.route('/')
def home():
    return "PING - I am alive!"


@app.route('/payment', methods=['POST'])
def charge_handle():
    print(request.data.decode('utf-8'))
    if not request.json:
        abort(400)
    print("Request dictionary: {}".format(request.json))

    data = request.json

    if data['email'] != None and data['stripe_cust_id'] != None and data['customer_name'] != None \
            and data['product_name'] != None and data['subs_price'] != None and data['subs_interval'] != None \
            and data['payment_status'] != None and data['failure_message'] != None:
        event_args = {}
        if data['payment_status'] == 'succeeded':
            event_args = {
                "user_id": str(data['email']),
                "event_type": "Success payment",
                "event_properties": {
                    "product_name": data['product_name'],
                    "subscription_interval": data['subs_interval'],
                },
                "price": float(data['subs_price']),
                "quantity": 1,
                "revenue": float(data['subs_price']),
                "productId": data['product_name'],
                "revenueType": "Success Charge",
                "user_properties": {
                    "customer_name": data['customer_name'],
                }
            }

            indentify_args = {
                "user_id": str(data['email']),
                "user_properties": {
                    "$add": {
                        "#payments": 1,
                        "total_revenue_from_user": float(data['subs_price']),
                    },
                }
            }
            identify = amplitude_logger.create_ident(**indentify_args)
            amplitude_logger.log_ident(identify)



        elif data['payment_status'] == 'failed':
            event_args = {
                "user_id": str(data['email']),
                "event_type": "Failed Charge",
                "event_properties": {
                    "reason": data['failure_message'],
                    "product_name": data['product_name'],
                },
                "price": -float(data['subs_price']),
                "revenue": -float(data['subs_price']),
                "productId": data['product_name'],
                "revenueType": "Refund",
            }

        event = amplitude_logger.create_event(**event_args)
        # send event to amplitude
        amplitude_logger.log_event(event)

    return jsonify({'status': 'ok'}), 200

@app.route('/refund', methods=['POST'])
def refund_handle():
    print(request.data.decode('utf-8'))
    if not request.json:
        abort(400)
    print("Request dictionary: {}".format(request.json))

    data = request.json

    if data['email'] != None \
            and data['product_name'] != None and data['amount'] != None \
            and data['reason'] != None:
        event_args = {
            "user_id": str(data['email']),
            "event_type": "Refund",
            "event_properties": {
                "reason": data['reason'],
                "product_name": data['product_name'],
            },
            "price": -float(data['amount']),
            "revenue": -float(data['amount']),
            "productId": data['product_name'],
            "revenueType": "Refund",
        }
        event = amplitude_logger.create_event(**event_args)
        # send event to amplitude
        amplitude_logger.log_event(event)

        indentify_args = {
            "user_id": str(data['email']),
            "user_properties": {
                "$add": {
                    "#payments": -1,
                    "total_revenue_from_user": -float(data['amount']),
                },
            }
        }
        identify = amplitude_logger.create_ident(**indentify_args)
        amplitude_logger.log_ident(identify)

    return jsonify({'status': 'ok'}), 200

@app.route('/subs_cancell', methods=['POST'])
def cancel_handle():
    # TODO посылать event в Amplitude
    # TODO identify: remove product name from subscribed_to
    return "OK"

@app.route('/unsubscribed', methods=['POST'])
def unsubs_handle():
    # TODO посылать event в Amplitude
    # TODO identify: remove product name from subscribed_to
    return "OK"
