import requests
import json
import glob
import sys, os
import datetime
from discord import Webhook, RequestsWebhookAdapter
from .constants import DISCORD_WEBHOOK, DISCORD_MENTION, ACCEPTABLE_RESPONSE_TIME

DISCORD_USERNAME = 'API Alert Bot'

if DISCORD_MENTION:
    mention = f"<{DISCORD_MENTION}>"
else:
    mention = ""

def publish_message(message):
    baseURL = f"https://discordapp.com/api/webhooks/{DISCORD_WEBHOOK}"
    webhook = Webhook.from_url(baseURL, adapter=RequestsWebhookAdapter())
    webhook.send(message, username=DISCORD_USERNAME)


def publish_frontend_alert(error):
    now = datetime.datetime.utcnow()
    message = f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Frontend API alert
Triggered at {now}
Caused by: {error}
===============================================
"""
    publish_message(message)


def publish_graphql_alert(error):
    now = datetime.datetime.utcnow()
    report_url = "TBD"
    message = f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Problem with GraphQL API: {error}
Triggered at {now}
See report at {report_url}
===============================================
"""
    publish_message(message)


def publish_response_time_alert(query_name, time, errors):
    now = datetime.datetime.utcnow()
    message = f"""
+++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
API response time is slow for query {query_name}!
Acceptable: {ACCEPTABLE_RESPONSE_TIME} s, actual {time} s
Errors encountered: {' '.join(map(str, errors))}
Triggered at {now}
===============================================
"""
    publish_message(message)
