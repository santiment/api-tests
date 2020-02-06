import requests
import json
import glob
import sys, os
import datetime
from discord import Webhook, RequestsWebhookAdapter, File
from constants import DISCORD_WEBHOOK, DISCORD_USER_ID

def send_alert(error_message):
    if DISCORD_WEBHOOK:
        baseURL = "https://discordapp.com/api/webhooks/{}".format(DISCORD_WEBHOOK)
        webhook = Webhook.from_url(baseURL, adapter=RequestsWebhookAdapter())
        if DISCORD_USER_ID:
            mention = f"<@{DISCORD_USER_ID}>"
        else:
            mention = ""
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
        webhook.send(message, username='API Alert Bot')
