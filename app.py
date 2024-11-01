from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getIncomingMessage', methods=['POST'])
def whatsapp_webhook():
    data = request.form  # Twilio sends data as form-encoded
    sender = data.get('From', '').replace('whatsapp:', '')
    message_body = data.get('Body', '').strip()

    print(message_body)

    # Example response
    response_message = f"Hello, you sent: {message_body}"
    #send_whatsapp_message(sender, response_message)
    
    return jsonify({"status": "Received and responded"}), 200

# @app.route('/sendMessage', methods=['POST'])
# def whatsapp_webhook_sendMessage():
#     data = request.form  # Twilio sends data as form-encoded
#     sender = data.get('From', '').replace('whatsapp:', '')
#     message_body = data.get('Body', '').strip()

#     print(message_body)

#     # Example response
#     response_message = f"Hello, you sent: {message_body}"
#     #send_whatsapp_message(sender, response_message)
    
#     return jsonify({"status": "Received and responded"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
