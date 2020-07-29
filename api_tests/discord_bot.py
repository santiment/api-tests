import requests
import json
import glob
import sys, os
import datetime
from discord import Webhook, RequestsWebhookAdapter
from .constants import DISCORD_WEBHOOK, DISCORD_USER_ID

if DISCORD_WEBHOOK:
    baseURL = "https://discordapp.com/api/webhooks/{}".format(DISCORD_WEBHOOK)
    webhook = Webhook.from_url(baseURL, adapter=RequestsWebhookAdapter())
if DISCORD_USER_ID:
    mention = f"<@{DISCORD_USER_ID}>"
else:
    mention = ""
report_url = "https://jenkins.internal.santiment.net/job/Santiment/job/api-tests/job/master/Test_20Report/"

def send_frontend_alert(error_message):
    if error_message:
        message = f"""
++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Frontend API alert
Triggered at {datetime.datetime.now()}
Caused by: {error_message}
===============================================
"""
    else:
        message = f"{datetime.datetime.now()} Frontend API check success!"
    if DISCORD_WEBHOOK:
        webhook.send(message, username='API Alert Bot')

def send_metric_alert(error=None):
    if error:
        message = f"""
++++++++++++++++++++++++++++++++++++++++++++++++
{mention}
Problem with API: {error}
Triggered at {datetime.datetime.now()}
See report at {report_url}
===============================================
"""
    else:
        message = f"{datetime.datetime.now()} Metric API check success!"
    if DISCORD_WEBHOOK:
        webhook.send(message, username='API Alert Bot')
