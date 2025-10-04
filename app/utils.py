from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
import auth
import sessions


def ensure_valid_token(session_id: str) -> str:
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    now = datetime.now(timezone.utc)
    expires_at = session["expires_at"]
    
    if now >= expires_at - timedelta(minutes=5) :
        refresh_token = session["strava_refresh_token"]
        updated_refresh_token = auth.refresh_access_token(refresh_token)
        sessions.update_session_tokens(**updated_refresh_token)
        return session["strava_access_token"]
    else:
        return session["strava_access_token"]
