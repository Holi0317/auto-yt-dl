"""Handle OAuth from Google API."""
import argparse
import logging

from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

CLIENT_SECRETS_FILE = "client_id.json"
SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'
STORAGE_FILE = 'credentials'

logger = logging.getLogger('auth')


def get_cred():
    """
    Get authorized credentials object.

    If no credentials is stored or it is invalid,
    the authorization flow will run.
    """
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()
    storage = Storage(STORAGE_FILE)
    creds = storage.get()

    if not creds or creds.invalid:
        flow = flow_from_clientsecrets(
            CLIENT_SECRETS_FILE, scope=SCOPE)
        flow.params['access_type'] = 'offline'
        creds = tools.run_flow(flow, storage, flags)
        storage.put(creds)

    return creds

