# -*- coding: utf-8 -*-
import json, urllib
from flask import Flask, request, abort
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

access_token = 'EAAW895WLezkBAGisDrIsZBuazNgk2Ll8fnpjbtg1wXOrJu3aYyFVLrCg3ZABUD3S70vEZAWHsbeYR4lKSm8mrbIdkZAimsAo9FHEHkbZCZBW89Wy56mYWlDyTmD5bzQAFSscMNkBJxbH7KfaVGgCZAo5gIin0SQeBmLRvRzdIstSwZDZD'


@app.route("/", methods=["GET"])
def root():
    return "Hello World!"


# webhook for facebook to initialize the bot
@app.route('/webhook', methods=['GET'])
def get_webhook():

    if not 'hub.verify_token' in request.args or not 'hub.challenge' in request.args:
        abort(400)

    return request.args.get('hub.challenge')


@app.route('/webhook', methods=['POST'])
def post_webhook():
    data = request.json

    if data["object"] == "page":
        for entry in data['entry']:
            for messaging_event in entry['messaging']:

                if "message" in messaging_event:

                    sender_id = messaging_event['sender']['id']

                    if 'text' in messaging_event['message']:
                        message_text = messaging_event['message']['text']

                        # Accessing Google Spreadsheets
                        scope = ['https://spreadsheets.google.com/feeds']

                        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

                        gc = gspread.authorize(credentials)

                        wks = gc.open("Google Spreadsheet Database").sheet1

                        wks.insert_row([sender_id, str(datetime.now())], index=2)

                        # Fetch a cell range
                        cell_list = wks.range('A1:B7')

                        print(cell_list)

                        reply(sender_id, message_text)

    return "ok", 200


def reply(recipient_id, message_text):
    params = {
        "access_token": access_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    print data

    url = "https://graph.facebook.com/v2.6/me/messages?" + urllib.urlencode(params)
    r = requests.post(url=url, headers=headers, data=data)
