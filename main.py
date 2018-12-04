from flask import Flask
from flask import request
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
import json

app = Flask(__name__)


@app.route('/callback', methods = ['POST'])
def api_message():
    data = request.data
    print(data)


@app.route('/mpesa', methods = ['POST'])
def send_push_request():

    timestamp = str(time.strftime("%Y%m%d%H%M%S"))
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

    password = base64.b64encode(bytes(u'174379' + passkey + timestamp, 'UTF-8')).decode('UTF-8')

    consumer_key = "FlYVIVkqtno6joTyU045VDDChM39eWFq"
    consumer_secret = "9NuFmdRGLS1ZDAEk"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    y = json.loads(requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret)).text)

    access_token = "{}".format(y['access_token'])
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = { "Authorization": "Bearer {}".format(access_token)}
    request = {
        "BusinessShortCode": "174379",
        "Password": "{}".format(password),
        "Timestamp": "{}".format(timestamp),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA": "254792514037",
        "PartyB": "174379",
        "PhoneNumber": "254792514037",
        "CallBackURL": "https://peternjeru.co.ke/safdaraja/api/callback.php",
        "AccountReference": "account",
        "TransactionDesc": "account"
    }

    response = requests.post(api_url, json=request, headers=headers)

    return response.text


if __name__ == '__main__':
    app.run()