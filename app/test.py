import requests

url = "https://v-help-bot.onrender.com/whatsapp"

data = {
    "From": "whatsapp:+1234567890",
    "Body": "Hello bot!"
}

resp = requests.post(url, data=data)
print(resp.text)

