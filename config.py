from boto.s3.connection import S3Connection
import amplitude_logger
import os

# token = S3Connection(os.environ['D_KEY'], os.environ['A_KEY'])
# DISCORD_BOT_TOKEN = token.access_key
# AMPLITUDE_API_KEY = token.secret_key

DISCORD_BOT_TOKEN = 'Nzg5MDAxMTI2ODMzNDIyMzY3.X9rsjw.KZYMLKbd8i98siD-ajaOLsEOk_0'
AMPLITUDE_API_KEY = '298ceb9b6bdd0b7a60c27edafc7aed20'

# DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL = "postgres://anjyujjlcqgupd:f4776575e1d67ac5f10612f2af981c55464e6b6a9348f7c8c01666cd73548aa9@ec2-50-19-247-157.compute-1.amazonaws.com:5432/dakhb74dv1ma6f"

# initialize amplitude logger
amplitude_logger = amplitude_logger.AmplitudeLogger(api_key=AMPLITUDE_API_KEY)