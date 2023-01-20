from pathlib import Path

import html2text
import pickle
import os.path
import base64
from email.mime.text import MIMEText

from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from rohlik import PATH_DATA

PATH_CREDENTIALS = Path(__file__).parent.parent / 'credentials.json'
PATH_TOKEN = PATH_DATA / 'token.pickle'


class EmailService:
    def __init__(self, user_id, sender):
        self.user_id = user_id
        self.sender = sender
        self.service = call_gmail_api()

    def send_message(self, to: str, subject: str = "", text: str = ""):
        message = self.create_message(to, subject, text)
        try:
            message = self.service.users().messages().send(userId=self.user_id, body=message).execute()
            print('INFO: Message sent.')
            return message
        except errors.HttpError as error:
            print(f'An error occurred: {error}')

    def create_message(self, to, subject, message_text):
        """Create a MIMEText message.
        Args:
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = self.sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}

    def get_messages(self, query):
        try:
            return self.service.users().messages().list(userId=self.user_id, q=query).execute()
        except Exception as error:
            print(f'An error occurred: {error}')

    def get_message(self, msg_id):
        try:
            return self.service.users().messages().get(userId=self.user_id, id=msg_id, format="full").execute()
        except Exception as error:
            print(f'An error occurred: {error}')
            return 1

    def get_message_with_keyword(self, sender, keyword, msg_num):
        k = 0
        body = ""
        messages = self.get_messages(sender)
        for message in messages['messages']:
            message = self.get_message(message['id'])
            msg_body = get_message_body(message)
            if keyword in msg_body:
                body = msg_body
                if k == msg_num:
                    break
                k += 1
        return html_to_text(body).replace("×", "*").replace("\xa0", "")


def call_gmail_api():
    scopes = ['https://mail.google.com/']
    credentials = None

    if os.path.exists(PATH_TOKEN):
        with open(PATH_TOKEN, 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(PATH_CREDENTIALS), scopes)
            credentials = flow.run_local_server(port=0)
        with PATH_TOKEN.open('wb') as token:
            pickle.dump(credentials, token)

    return build('gmail', 'v1', credentials=credentials)


def get_message_body(message):
    """This took me 6 hours."""
    return base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data'].encode('utf8')).decode('utf8')


def html_to_text(html):
    return html2text.html2text(html)
