import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
import google.auth

# If modifying these scopes, delete the file token.json.
# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# def gmail_authenticate():
#   """Shows basic usage of the Gmail API.
#   Lists the user's Gmail labels.
#   """
#   creds = None
#   # The file token.json stores the user's access and refresh tokens, and is
#   # created automatically when the authorization flow completes for the first
#   # time.
#   if os.path.exists("token.json"):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#   # If there are no (valid) credentials available, let the user log in.
#   if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#       creds.refresh(Request())
#     else:
#       flow = InstalledAppFlow.from_client_secrets_file(
#           "credentials.json", SCOPES
#       )
#       creds = flow.run_local_server(port=8000)
#     # Save the credentials for the next run
#     with open("token.json", "w") as token:
#       token.write(creds.to_json())
#   return build('gmail', 'v1', credentials=creds)

# Authentication and service creation
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    # token.json stored user access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Authentication if no valid credentials are available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This credentials.json is the credential you download from Google API portal when you 
            # created the OAuth 2.0 Client IDs
            flow = InstalledAppFlow.from_client_secrets_file(
                './polls/credentials.json', SCOPES)
            # this is the redirect URI which should match your API setting, you can 
            # find this setting in Credentials/Authorized redirect URIs at the API setting portal
            creds = flow.run_local_server(port=8001)
            # creds = flow.run_console()
        # Save vouchers for later use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

  # try:
  #   # Call the Gmail API
  #   service = build("gmail", "v1", credentials=creds)
  #   results = service.users().labels().list(userId="me").execute()
  #   labels = results.get("labels", [])

  #   if not labels:
  #     print("No labels found.")
  #     return
  #   print("Labels:")
  #   for label in labels:
  #     print(label["name"])

  # except HttpError as error:
  #   # TODO(developer) - Handle errors from gmail API.
  #   print(f"An error occurred: {error}")

# Create and send emails
def send_message(service, sender, to, subject, msg_html):
    message = MIMEMultipart('alternative')
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    msg = MIMEText(msg_html, 'html')
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message = (service.users().messages().send(userId="me", body=body).execute())
    print(f"Message Id: {message['id']}")

# Using Gmail API
# service = gmail_authenticate()
# send_message(service, "jourdan.ljxx@gmail.com", "jingxuan.li@duke.edu", "Test Email", "<h1>Your ride has been confirmed by a driver</h1>")


# def gmail_send_message():
#   """Create and send an email message
#   Print the returned  message id
#   Returns: Message object, including message id

#   Load pre-authorized user credentials from the environment.
#   TODO(developer) - See https://developers.google.com/identity
#   for guides on implementing OAuth2 for the application.
#   """
#   creds, _ = google.auth.default()

#   try:
#     service = gmail_authenticate()
#     message = EmailMessage()

#     message.set_content("This is automated draft mail")

#     message["To"] = "jingxuan.li@duke.edu"
#     message["From"] = "jourdan.ljxx@gmail.com"
#     message["Subject"] = "Automated draft"

#     # encoded message
#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#     create_message = {"raw": encoded_message}
#     # pylint: disable=E1101
#     send_message = (
#         service.users()
#         .messages()
#         .send(userId="me", body=create_message)
#         .execute()
#     )
#     print(f'Message Id: {send_message["id"]}')
#   except HttpError as error:
#     print(f"An error occurred: {error}")
#     send_message = None
#   return send_message


# if __name__ == "__main__":
#   gmail_authenticate()
#   # gmail_send_message()
