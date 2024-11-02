from flask import Flask, request, jsonify, send_file
import os
import requests
import json
import io
from google.cloud import storage
import pandas as pd
import csv

app = Flask(__name__)

VERIFY_TOKEN = "turmerik_token"

storage_client = storage.Client()

def get_all_user_data():
    bucket = storage_client.bucket('turmerik_user_data')
    blobs = bucket.list_blobs()

    user_data_list = []

    for blob in blobs:
        if blob.name.endswith('.json'):
            data = json.loads(blob.download_as_string())
            user_data_list.append(data)

    return user_data_list

def export_to_csv(user_data_list):
    if not user_data_list:
        print("No user data found.")
        return
    output = io.StringIO()
    keys = set().union(*(d.keys() for d in user_data_list))
    dict_writer = csv.DictWriter(output, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(user_data_list)
    output.seek(0)
    return output
    

def export_to_excel(user_data_list, output_file):
    if not user_data_list:
        print("No user data found.")
        return
    output = io.BytesIO()
    df = pd.DataFrame(user_data_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='UserData')
    output.seek(0)
    return output

def get_conversation_state(sender):
    # Get the state of the conversation
    bucket = storage_client.bucket("turmerik_user_data")
    blob = bucket.blob(f"{sender}.json")
    if blob.exists():
        user_data = json.loads(blob.download_as_string())
        user_state = user_data.get("state")
    else:
        user_state = "user_name"
        user_data = {"state": "user_name", "name": "", "dob": "", "gender": "", "address": "", "medical_history": "", "current_medications": ""}
        blob.upload_from_string(
            data = json.dumps(user_data),
            content_type='application/json'
        )
    return user_state, user_data

def save_conversation_state(sender, user_data):
    bucket = storage_client.bucket("turmerik_user_data")
    blob = bucket.blob(f"{sender}.json")
    blob.upload_from_string(
        data=json.dumps(user_data),
        content_type='application/json'
    )

def send_whatsapp_message(to_number, message_body, template_name):
    url = f"https://graph.facebook.com/v21.0/440893352449295/messages"
    
    headers = {
        'Authorization': f'Bearer {os.environ.get("META_ACCESS_TOKEN")}',
        'Content-Type': 'application/json',
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",  
        "text": {
            "body": message_body  
        }
    }

    data_template = {
        "messaging_product": "whatsapp",
        "to": to_number, 
        "type": "template", 
        "template": { 
            "name": template_name, 
            "language": { "code": "en" } 
        } 
    }

    if template_name:
        response = requests.post(url, headers=headers, json=data_template)
    else:
        response = requests.post(url, headers=headers, json=data)
    
    return response.json()

@app.route('/getIncomingMessage', methods=['POST','GET'])
def whatsapp_webhook():
    # Handle the verification of the webhook. Whatsapp Business API Requires us to make sure that the webhook is valid by sending a challenge back.
    if request.method == "GET":
        # Verify token validity
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403
    
    # Handle incoming messages
    if request.method == "POST":
        # Extract data from the request
        data = json.loads(request.get_data(as_text=True))
        # Extract sender and message body
        try:
            sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            message_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        except (KeyError, IndexError) as e:
            print("Error extracting data:", e)
            return jsonify({"status": "Error extracting data"}), 400

        # Get the State of the current User and determine the next course of action.
        user_state, user_data = get_conversation_state(sender)

        if user_state == "user_name":
            user_data["name"] = message_body
            user_data["state"] = "dob"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Please enter your date of birth in the format DD/MM/YYYY", None)
        elif user_state == "dob":
            user_data["dob"] = message_body
            user_data["state"] = "gender"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Please enter your gender(M for Male, F for Female, O for other)", None)
        elif user_state == "gender":
            user_data["gender"] = message_body
            user_data["state"] = "address"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Please enter your address", None)
        elif user_state == "address":
            user_data["address"] = message_body
            user_data["state"] = "medical_history"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Please enter your medical history separated by a comma (example: High Blood Pressure, Heart Condition). If you don't have any medical history, please enter None", None)
        elif user_state == "medical_history":
            user_data["medical_history"] = message_body
            user_data["state"] = "current_medications"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Please enter your current medications separated by a comma (example: Aspirin, Metformin). If you don't have any current medications, please enter None", None)
        elif user_state == "current_medications":
            user_data["current_medications"] = message_body
            user_data["state"] = "completed"
            save_conversation_state(sender, user_data)
            send_whatsapp_message(sender, "Thank you for providing your information. We will get back to you shortly", None)
        elif user_state == "completed":
            send_whatsapp_message(sender, "Thank you for providing your information. We will get back to you shortly", None)
        return jsonify({"status": "Received and responded"}), 200
    
    return jsonify({"status": "Received and responded"}), 200

@app.route('/startConversation', methods=['POST'])
def start_conversation():
    target_audience = request.json.get("target_audience")
    template_name = 'turmerik_start_convo'
    print(send_whatsapp_message(target_audience, "", template_name))
    return jsonify({"status": "Conversation started"}), 200

@app.route('/extractData', methods=['GET'])
def extract_data():
    format_requested = request.args.get("format")
    if format_requested == "csv":
        output_file = "user_data.csv"
        csv_file = export_to_csv(get_all_user_data(), output_file)
        return send_file(
            io.BytesIO(csv_file.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename='user_data.csv'
        )
    elif format_requested == "excel":
        output_file = "user_data.xlsx"
        excel_file = export_to_excel(get_all_user_data(), output_file)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            attachment_filename='user_data.xlsx'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)



