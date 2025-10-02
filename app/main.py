from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi import Cookie, HTTPException
import auth
import sessions
import config
from datetime import datetime, timezone, timedelta
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    #Serves the login page
    return FileResponse("static/login.html")

@app.get("/login")
async def login():
    #Redirects user to Strava authorization page
    auth_url = auth.get_strava_auth_url()
    return RedirectResponse(auth_url)


@app.get("/dashboard")
async def dashboard(code: str = None, error: str = None):
    # User denied authorization
    if error:
        return RedirectResponse("/static/login.html")
    
    # Missing authorization code
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    # Exchange code for tokens
    try:
        token_data = auth.exchange_code_for_token(code)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Strava authorization failed: {str(e)}")
    
    # Convert Unix timestamp to datetime
    expires_at = datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
    
    # Create session
    session_id = sessions.create_session(
        user_info=token_data["athlete"],
        strava_access_token=token_data["access_token"],
        strava_refresh_token=token_data["refresh_token"],
        expires_at=expires_at
    )
    
    # Set cookie and redirect to dashboard page
    response = RedirectResponse("/static/dashboard.html")
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True
    )
    return response
        

@app.get("/user")
async def get_user(session_id:str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session["user_info"]
    
@app.get("/activities")
async def get_activities(session_id: str = Cookie(None)):
    # Validate session
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Get Strava access token
    access_token = session["strava_access_token"]
    
    # Calculate time range (last 7 days)
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    # Set up API request
    url = f"{config.STRAVA_API_BASE_URL}/athlete/activities"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "before": int(now.timestamp()),
        "after": int(week_ago.timestamp()),
        "per_page": 30
    }
    
    # Call Strava API
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        activities = response.json()
        
        # Calculate total distance for runs
        total_distance = sum(
            activity.get("distance", 0) 
            for activity in activities 
            if activity.get("type") == "Run"
        )
        
        return total_distance
        
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Strava API error: {str(e)}")


@app.post("/logout")
async def logout(session_id: str = Cookie(None)):
    # If no session cookie, they're already "logged out"
    if not session_id:
        response = JSONResponse(content={"message": "Already logged out"})
        response.delete_cookie(key=config.SESSION_COOKIE_NAME)
        return response
    
    # Delete the session (returns True or False, but we don't care)
    sessions.delete_session(session_id)
    
    # Return success and clear cookie
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key=config.SESSION_COOKIE_NAME)
    return response
