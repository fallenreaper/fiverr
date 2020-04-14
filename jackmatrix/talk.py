import requests
import json
import datetime

host = "3.21.113.195:5000"
sub = '/api/v1.0/notification'

url = f'http://{host}' + sub


payload = {
    'discord_id': '136612629044002816',
    'message': 'Test message!',
    'timestamp': '1586058800'
}

# print(datetime.datetime.utcnow().timestamp())
x = requests.post(url, data=payload)
print(x.text)

