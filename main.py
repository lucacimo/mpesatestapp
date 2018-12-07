from flask import Flask
from flask import request, render_template, session
from flask_wtf import FlaskForm
from flask_socketio import SocketIO
from wtforms import StringField, SubmitField, IntegerField, ValidationError
from wtforms.validators import DataRequired, NumberRange
import phonenumbers
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
socketio = SocketIO(app)

transactions = {}


def validate_phone(form, field):
    number = phonenumbers.parse(field.data)
    if not phonenumbers.is_valid_number(number) and number.country_code != "254":
        raise ValidationError('The phone number must be in the format 254+XXXXXXXXX')


class MpesaForm(FlaskForm):
    phone = StringField('Phone number', validators=[DataRequired(), validate_phone],
                        render_kw={"placeholder": "+254XXXXXXXX"})

    amount = IntegerField('Amount (KES)', validators=[DataRequired(),
                                                      NumberRange(min=0, max=70000,
                                                      message="You can transfer up to 70000 KES ")],
                          render_kw={"placeholder": "(KHS 0-70000)"})

    submit = SubmitField('Submit')


@socketio.on('connection')
def handle_my_custom_event(message):
    print(message)


@socketio.on('submission')
def handle_my_custom_event(message):
    message = json.loads(message)
    phone_number = message['phone_number'].replace("+", "")
    amount = message['amount']
    timestamp = str(time.strftime("%Y%m%d%H%M%S"))
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    password = base64.b64encode(bytes(u'174379' + passkey + timestamp, 'UTF-8')).decode('UTF-8')

    consumer_key = "FlYVIVkqtno6joTyU045VDDChM39eWFq"
    consumer_secret = "9NuFmdRGLS1ZDAEk"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    y = json.loads(requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret)).text)

    access_token = "{}".format(y['access_token'])
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer {}".format(access_token)}
    body = {
        "BusinessShortCode": "174379",
        "Password": "{}".format(password),
        "Timestamp": "{}".format(timestamp),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "{}".format(amount),
        "PartyA": "{}".format(phone_number),
        "PartyB": "174379",
        "PhoneNumber": "{}".format(phone_number),
        "CallBackURL": "https://mpesatestapp.herokuapp.com/callback",
        "AccountReference": "account",
        "TransactionDesc": "account"
    }

    response = requests.post(api_url, json=body, headers=headers)
    response = json.loads(response.text)
    if response['ResponseCode'] == '0':
        transactions[response['CheckoutRequestID']] = request.sid

    print(transactions)


@app.route('/callback', methods=['POST'])
def api_message():
    data = json.loads(request.data)
    checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']
    result = data['Body']['stkCallback']['ResultCode']
    print(checkout_request_id)
    print(result)

    if result == "0":
        message = "The Payment with transaction Id " + "{}".format(checkout_request_id) + " was successful"

    else:
        message = "The Payment with transaction Id " + "{}".format(checkout_request_id) + " failed"

    sid = transactions[checkout_request_id]
    socketio.emit("completed", message, room=sid)


@app.route('/', methods=['GET', 'POST'])
def submit():
    form = MpesaForm()
    return render_template('mpesaform.html', title='Mpesa Payment', form=form)


if __name__ == '__main__':
    socketio.run(app)