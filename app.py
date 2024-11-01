from flask import Flask, request, jsonify
from twilio.rest import Client
import os

app = Flask(__name__)

os.getenv("CLAUDE_API_KEY")

account_sid = os.getenv("ACCOUNT_SID") 
auth_token = os.getenv("ACCOUNT_API_KEY")    
whatsapp_number = 'whatsapp:+14155238886' 

client = Client(account_sid, auth_token)

@app.route('/getIncomingMessage', methods=['POST'])
def whatsapp_webhook():
    data = request.form  # Twilio sends data as form-encoded
    sender = data.get('From', '').replace('whatsapp:', '')
    message_body = data.get('Body', '').strip()

    print(message_body)

    message_sid = send_whatsapp_message("+14708386790", message_body)
    print(message_sid)
    # Example response
    response_message = f"Hello, you sent: {message_body}"
    #send_whatsapp_message(sender, response_message)
    
    return jsonify({"status": "Received and responded"}), 200

# Function to send a WhatsApp message
def send_whatsapp_message(to, message):
    message = client.messages.create(
        body=message,
        from_=whatsapp_number,
        to=f'whatsapp:{to}'
    )
    return message.sid

# Route to trigger sending a message
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    recipient_number = data.get('phone')
    message_body = data.get('message')

    if recipient_number and message_body:
        # Send the message
        message_sid = send_whatsapp_message(recipient_number, message_body)
        return jsonify({"status": "Message sent", "sid": message_sid}), 200
    else:
        return jsonify({"error": "Phone number and message are required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

