import requests
from server_script.local_line_settings import token

url = "https://api.line.me/v2/bot/message/push"
id = "Ueb9b25b83cdec3349bf98e00b05afff6"
text='walao weh'

def send_line_notif(msg,userid):
	headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer "+token
}
	data = { 
	"to": userid,
	"messages": [
		{
			"type": "text",
			"text": msg
		}
	]
}
	response = requests.post(url, headers=headers, json=data)
	return response
