import requests
import json
import glob
import sys, os
import datetime
from discord import Webhook, RequestsWebhookAdapter
from .constants import DISCORD_WEBHOOK, DISCORD_USER_ID

DISCORD_USERNAME = 'API Alert Bot'

if DISCORD_USER_ID:
    mention = f"<@{DISCORD_USER_ID}>"
else:
    mention = ""

def publish_message(message):
    baseURL = "https://discordapp.com/api/webhooks/{}".format(DISCORD_WEBHOOK)
    webhook = Webhook.from_url(baseURL, adapter=RequestsWebhookAdapter())
    webhook.send(message, username=DISCORD_USERNAME)

def publish_frontend_alert(error):
    now = datetime.datetime.utcnow()

    if error:
        message = build_frontend_error_message(mention, error, now)
    else:
        message = build_frontend_success_message(triggered_at)

    publish_message(message)


def build_frontend_error_message(mention, error, triggered_at):
    now = datetime.datetime.utcnow()
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

def publish_graphql_alert(error=None):
    report_url = "https://jenkins.internal.santiment.net/job/Santiment/job/api-tests/job/master/Test_20Report/"
    now = datetime.datetime.utcnow()
    if error:
        message = build_graphql_error_message(mention, error, now)
    else:
        message = build_graphql_success_message(now)

    publish_message(message)