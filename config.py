from boto.s3.connection import S3Connection
import amplitude_logger
import os

token = S3Connection(os.environ['D_KEY'], os.environ['A_KEY'])
DISCORD_BOT_TOKEN = token.access_key
AMPLITUDE_API_KEY = token.secret_key

DATABASE_URL = os.environ['DATABASE_URL']

STRIPE_KEY = os.environ['STRIPE_KEY']

# initialize amplitude logger
amplitude_logger = amplitude_logger.AmplitudeLogger(api_key=AMPLITUDE_API_KEY)
