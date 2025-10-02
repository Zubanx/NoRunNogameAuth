import config
from urllib.parse import urlencode  
import requests


def get_strava_auth_url() -> str:
    """Builds the URL to redirect users to Strava's authorization page."""
    params = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "activity:read_all,activity:write"
    }
    query = urlencode(params)
    return f"{config.STRAVA_AUTHORIZE_URL}?{query}"

    
def exchange_code_for_token(code: str) -> dict:
    """
    Exchanges authorization code for access token and user data.
    Raises Exception if the exchange fails.
    """
    params = {
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.REDIRECT_URI 
    }
    
    try:
        response = requests.post(config.STRAVA_TOKEN_URL, data=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Strava token exchange failed: {response.status_code} - {response.text}")
            
    except requests.RequestException as e:
        raise Exception(f"Failed to connect to Strava: {str(e)}")