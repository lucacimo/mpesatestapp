from flask import Flask
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
import json

app = Flask(__name__)


@app.route('/krafty', methods = ['POST'])
def api_message():
    data = request.data
    print(data)
    return "already run"


timestamp = str(time.strftime("%Y%m%d%H%M%S"))

password = base64.b64encode(bytes(u'174379' + 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' + timestamp, 'UTF-8')).decode('UTF-8')


consumer_key = "FlYVIVkqtno6joTyU045VDDChM39eWFq"
consumer_secret = "9NuFmdRGLS1ZDAEk"
api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

y = json.loads(requests.get(api_URL, auth=HTTPBasicAuth(consumer_key,consumer_secret)).text)

print(y['access_token'])

# import pdb; pdb.set_trace()

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



response = requests.post(api_url, json = request, headers=headers)

print(response.text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)