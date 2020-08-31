import requests
import json
import glob
import sys, os
import datetime
from discord import Webhook, RequestsWebhookAdapter
from .constants import DISCORD_WEBHOOK, DISCORD_USER_ID, ACCEPTABLE_RESPONSE_TIME

DISCORD_USERNAME = 'API Alert Bot'

if DISCORD_USER_ID:
    mention = f"<@{DISCORD_USER_ID}>"
else:
    mention = ""

def publish_message(message):
    baseURL = f"https://discordapp.com/api/webhooks/{DISCORD_WEBHOOK}"
    webhook = Webhook.from_url(baseURL, adapter=RequestsWebhookAdapter())
    webhook.send(message, username=DISCORD_USERNAME)

def publish_frontend_alert(error):
    now = datetime.datetime.utcnow()

    if error:
        message = build_frontend_error_message(mention, error, now)
    else:
        message = build_frontend_success_message(now)

    publish_message(message)

def publish_graphql_alert(error=None):
    now = datetime.datetime.utcnow()

    if error:
        message = build_graphql_error_message(mention, error, now)
    else:
        message = build_graphql_success_message(now)

    publish_message(message)

def publish_response_time_alert(time, errors):
    now = datetime.datetime.utcnow()
    errors_str = ' '.join(map(str, errors))
    message = build_response_time_error_message(mention, time, errors_str, now)
    publish_message(message)

def build_frontend_error_message(mention, error, triggered_at):
    return f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Frontend API alert
Triggered at {triggered_at}
Caused by: {error}
===============================================
"""

def build_frontend_success_message(triggered_at):
    return f"{triggered_at} Frontend API check success!"

def build_graphql_error_message(mention, error, triggered_at):
    report_url = "TBD"
    return f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Problem with GraphQL API: {error}
Triggered at {triggered_at}
See report at {report_url}
===============================================
"""

def build_graphql_success_message(triggered_at):
    return f"{triggered_at} GraphQL API check success!"

def build_response_time_error_message(mention, time, errors_str, triggered_at):
    return f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
API response time is slow!
Expected {ACCEPTABLE_RESPONSE_TIME} s, actual {time} s
Errors encountered: {errors_str}
Triggered at {triggered_at}
===============================================
"""