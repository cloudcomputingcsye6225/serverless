import base64
import os
import json
import requests
from sqlalchemy import create_engine, MetaData, Table


def send_verification_email(data):
    message = json.loads(data)
    user_id = message['id']

    domain_name = "generalming.me"
    port_number = "8888"
    verification_link = f"https://{domain_name}/verify/{user_id}"

    email_subject = "Verify Your Email Address"
    email_body = f"Click the following link to verify your email address: {verification_link}"

    mailgun_api_key = "a41b902655d5bc8b9fae7cb499c1590a-f68a26c9-e52a5bd0"
    mailgun_domain = domain_name
    sender_email = f"verification@{domain_name}"
    recipient_email = message['username']

    track(user_id)

    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={"from": sender_email,
              "to": recipient_email,
              "subject": email_subject,
              "text": email_body})

    if response.status_code == 200:
        print(f"Email verification link sent to {recipient_email}.")
    else:
        print(f"Failed to send verification email to {recipient_email}. Status code: {response.status_code}")

def track(user_id):
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    DATABASE_USER = os.environ.get('DATABASE_USER')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    DATABASE_HOST = os.environ.get('DATABASE_HOST')

    engine = create_engine(f'mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}')
    
    metadata = MetaData()
    metadata.reflect(bind=engine)
    users_table = metadata.tables['users']

    query = users_table.select().where(users_table.c.verification_link == user_id)
    connection = engine.connect()
    result = connection.execute(query)

    user_record = result.fetchone()
    connection.close()
    res = {}
    res['token'] = user_record._mapping['verification_link']
    res['ttl'] = user_record._mapping['expiration_time']
    res['username'] = user_record._mapping['username']
    res['verification_status'] = user_record._mapping['is_verified']
    
    
    if user_record:
        print(res)
    else:
        print(f"No user found with token {user_id}")

def verify_email(event, context):
    data = base64.b64decode(event['data'])
    send_verification_email(data)
    return "Email verification process initiated."
    
