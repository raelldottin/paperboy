import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def get_google_cloud_token(client_secret_file, scopes):
    """
    Obtain OAuth2 token from Google Cloud using the client secret file.

    :param client_secret_file: Path to the client secret JSON file downloaded from Google Cloud Console.
    :param scopes: List of scopes for which the token is required.
    :return: Token (str)
    """

    # Use the client secret file to start the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)

    # Launch a local web server to handle the OAuth redirect
    creds = flow.run_local_server(port=54543)

    # The token will be available in the credentials object
    return creds.token

if __name__ == "__main__":
    CLIENT_SECRET_FILE = "client_secret.json"
    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    token = get_google_cloud_token(CLIENT_SECRET_FILE, SCOPES)
    print(f"OAuth2 Token: {token}")
