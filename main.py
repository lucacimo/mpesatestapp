from flask import Flask
from flask import request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, ValidationError
from wtforms.validators import DataRequired, NumberRange
import phonenumbers
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


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


@app.route('/callback', methods=['POST'])
def api_message():
    data = request.data
    print(data)
    return "Success"


@app.route('/', methods=['GET', 'POST'])
def submit():
    form = MpesaForm()
    if form.validate_on_submit():
        api_url = "http://0.0.0.0:5000/mpesa"
        phone_number = form.phone.data.replace("+", "")
        body = {
                "phone_number": "{}".format(phone_number),
                "amount": "{}".format(form.amount.data),
        }
        response = requests.post(api_url, json=body)
        return response.text

    return render_template('mpesaform.html', title='Mpesa Payment', form=form)


@app.route('/mpesa', methods = ['POST'])
def send_push_request():
    phone_number = request.json.get('phone_number')
    amount = request.json.get('amount')

    timestamp = str(time.strftime("%Y%m%d%H%M%S"))
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    password = base64.b64encode(bytes(u'174379' + passkey + timestamp,'UTF-8')).decode('UTF-8')

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
        "CallBackURL": "https://peternjeru.co.ke/safdaraja/api/callback.php",
        "AccountReference": "account",
        "TransactionDesc": "account"
    }

    response = requests.post(api_url, json=body, headers=headers)

    return response.text


if __name__ == '__main__':
    app.run()