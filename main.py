from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import requests
import logging

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
    logging.info("Inside the webhook method in the server!")
    logging.info("Request Method:", request.method)
    logging.info("Request Method:", request.method)
    logging.info("Request URL:", request.url)
    logging.info("Request Headers:", request.headers)
    logging.info("Request Body:", request.get_data(as_text=True))  
    logging.info("Request Args:", request.args)  
    logging.info("Request Form:", request.form)
    if request.method == "GET":
        # Verify token logic
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403
    
    if request.method == "POST":
        incoming_data = request.json

        logging.info("Inside the post method in the server!")

        # Log the incoming data (optional)
        logging.info("Incoming Data: %s", incoming_data)

        # Check if the data contains the 'value' key with 'messages'
        if 'value' in incoming_data:
            value = incoming_data['value']

            print("Inside Extract message")

            # Extract messages
            messages = value.get('messages', [])
            for message in messages:
                from_number = message.get('from')  # Sender's number
                message_id = message.get('id')      # Message ID
                timestamp = message.get('timestamp') # Message timestamp
                message_body = message.get('text', {}).get('body') 
            print(send_whatsapp_message(from_number, message_body))
            return jsonify({"status": "Received and responded", "message_body": message_body}), 200
    
    return jsonify({"status": "No messages received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)



