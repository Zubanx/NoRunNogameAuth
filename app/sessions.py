from datetime import datetime
from typing import Optional, Dict
import secrets
from fastapi import HTTPException

_session_store: Dict[str, dict] = {}

def create_session(user_info: dict, strava_access_token: str, 
                   strava_refresh_token: str, expires_at: datetime) -> str:
    session_id = secrets.token_urlsafe(32)

    _session_store[session_id] = {
        "user_info": user_info,
        "strava_access_token" : strava_access_token,
        "strava_refresh_token" : strava_refresh_token,
        "expires_at" : expires_at
    }
    return session_id
    

def get_session(session_id: str) -> Optional[dict]:
    return _session_store.get(session_id)

def delete_session(session_id: str) -> bool:
    if session_id in _session_store:
        del _session_store[session_id]
        return True
    return False

def update_session_tokens(session_id: str, access_token: str, 
                         refresh_token: str, expires_at: datetime) -> bool:
   
    session = get_session(session_id)
    if session:
        session["strava_access_token"] = access_token
        session["strava_refresh_token"] = refresh_token
        session["expires_at"] = expires_at
        return True
    return False
    
    