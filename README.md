# WhatsApp Bot for Collecting User Data

## Project Overview
This project is a WhatsApp bot designed to collect sensitive medical data from users and securely store it for healthcare providers. The bot interacts with users to collect essential information and allows healthcare providers to download this data in various formats (Excel, CSV). The backend is built using Flask, hosted on Google Cloud Run, and utilizes Google Cloud Storage with end-to-end encryption for data security.

## Features
- **User Interaction**: The bot collects user data, including name, date of birth, gender, address, medical condition, and current medication.
- **Intuitive Flow**: The bot guides users step-by-step to make the data collection process smooth and easy to follow.
- **Secure Data Access**: Healthcare providers can download the collected data securely in formats like Excel or CSV.
- **Data Security**: The bot ensures high data security through AES encryption for data at rest, HTTPS for data in transit, and password-protected file downloads.

## Table of Contents
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Setup

1. **Create a Meta Business Account**: Begin by setting up a Meta Business account to access the WhatsApp Business API. This setup includes configuring message templates and API authorization to enable seamless interaction.

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/kslohith/Turmerik-Bot
   cd Turmerik-bot

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt

4. **Run Locally**:
    ```bash
    python3 main.py

When running locally we need to manually create a .env file and add environment variables that we are using namely 
1. META_ACCESS_TOKEN
2. ZIP_PASSWORD
3. Google Cloud Service account to interact with GCP suite of products including storage buckets.

The same 3 environment variables need to be configured on GCP or any cloud provider.

## API Endpoints

1. **/startConversation**:
Method: POST
Description: Initiates a conversation with a user by sending an introductory message.

2. **/getIncomingMessages**:
Method: POST
Description: This webhook endpoint listens for incoming messages from users. Based on the user's conversation state, the bot responds and progresses through the data collection flow.

3. **/extractData**:
Method: GET
Description: Allows healthcare providers to download collected data in Excel or CSV formats. Files are password-protected for additional security.
Output: A password-protected file with the requested format.

Security Measures
Data security is a top priority, with multiple layers of protection in place:

Encryption at Rest: Data is stored in Google Cloud Storage using AES encryption to protect it at rest.
Encryption in Transit: HTTPS is enforced for all communication to safeguard data in transit.
Password-Protected File Downloads: Data exports are password-protected, and the password is rotated daily to maintain high security.


## License

This project is licensed under the MIT License. For more details, see the LICENSE file in this repository.