from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleMail(object):
    def __init__(self, credential_path: str = 'credentials.json', scopes: list = ['https://www.googleapis.com/auth/gmail.readonly']):
        assert os.path.exists(credential_path), f'{credential_path} is not a valid path'
        self.__service = build('gmail', 'v1', credentials=self.__authenticate(credential_path))
        self.__users = self.__service.users() # pylint: disable=maybe-no-member
        self.__fields = {
            'labels': self.__users.labels, # pylint: disable=maybe-no-member
            'messages': self.__users.messages, # pylint: disable=maybe-no-member
            # 'history': self.__users.history, # pylint: disable=maybe-no-member
            'drafts': self.__users.drafts # pylint: disable=maybe-no-member
        }
        self.__available_options = {
            'labels': ['userId'],
            'messages': ['id', 'userId', 'includeSpamTrash', 'maxResults', 'pageToken', 'q', 'format'],
            # 'history': ['userId', 'includeSpamTrash', 'labelIds', 'maxResults', 'pageToken', 'q'],
            'drafts': ['userId', 'includeSpamTrash', 'maxResults', 'pageToken', 'q']
        }
        
    def __authenticate(self, credential_path: str, scopes: list = ['https://www.googleapis.com/auth/gmail.readonly']):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credential_path, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def list_(self, field: str, options: dict = {'userId': 'me'}):
        for key in options.keys():
            assert key in self.__available_options[field], f'Invalid options type given {key}. Expected one of {self.__available_options[field]}'
        default_options = {'userId': 'me'}
        default_options.update(options)
        response = self.__fields[field]().list(**default_options).execute()
        return response.get(field, [])

    def get_(self, field: str, options: dict = {'userId': 'me'}):
        for key in options.keys():
            assert key in self.__available_options[field], f'Invalid options type given {key}. Expected one of {self.__available_options[field]}'
        default_options = {'userId': 'me'}
        default_options.update(options)
        response = self.__fields[field]().get(**default_options).execute()
        return response