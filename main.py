from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import requests
import json

app = Flask(__name__)

VERIFY_TOKEN = "turmerik_token"

def send_whatsapp_message(to_number, message_body):
    print("Inside send_whatsapp_message", to_number, message_body)
    url = f"https://graph.facebook.com/v21.0/440893352449295/messages"
    
    headers = {
        'Authorization': f'Bearer {os.environ.get("META_ACCESS_TOKEN")}',
        'Content-Type': 'application/json',
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "type": "text",  
        "text": {
            "body": message_body  
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    return response.json()

@app.route('/getIncomingMessage', methods=['POST','GET'])
def whatsapp_webhook():
    print("Inside the webhook method in the server!", flush=True)
    print("Request Method:", request.method, flush=True)
    print("Request Method:", request.method, flush=True)
    print("Request URL:", request.url, flush=True)
    print("Request Headers:", request.headers, flush=True)
    print("Request Body:", request.get_data(as_text=True), flush=True)  
    print("Request Args:", request.args, flush=True)  
    print("Request Form:", request.form, flush=True)
    # if request.method == "GET":
    #     # Verify token logic
    #     token_sent = request.args.get("hub.verify_token")
    #     if token_sent == VERIFY_TOKEN:
    #         return request.args.get("hub.challenge")
    #     return "Verification token mismatch", 403

    data = json.loads(request.get_data(as_text=True))

    # Extract sender and message body
    try:
        sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        message_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        print("Sender:", sender)
        print("Message Body:", message_body)
    except (KeyError, IndexError) as e:
        print("Error extracting data:", e)
   
    print(send_whatsapp_message(sender, message_body))
    return jsonify({"status": "Received and responded", "message_body": message_body}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)



