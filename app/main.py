from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi import Cookie, HTTPException
import auth
import sessions
import config
from datetime import datetime, timezone, timedelta
import requests
import utils
from database import SessionLocal
from models_db import User, Session
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Goal(BaseModel):
    updated_goal: float

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



@app.get("/user")
async def get_user(session_id:str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session["user_info"]
    
@app.get("/check-goal")
async def check_goal(session_id: str = Cookie(None)):
    
    # Validation
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Get fresh access token (handles refresh if needed)
    access_token = utils.ensure_valid_token(session_id)
    
    # Get user's goal from database
    goal_miles = session["weekly_goal_miles"]
    
    # Calculate time range
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    # Call Strava API (ONCE!)
    url = f"{config.STRAVA_API_BASE_URL}/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "before": int(now.timestamp()),
        "after": int(week_ago.timestamp()),
        "per_page": 30
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        activities = response.json()
        
        # Calculate total distance in meters
        total_distance_meters = sum(
            activity.get("distance", 0) 
            for activity in activities 
            if activity.get("type") == "Run"
        )
        
        # Convert to miles
        actual_miles = total_distance_meters / 1609.344
        
        # Calculate goal status
        goal_met = actual_miles >= goal_miles
        remaining_miles = max(0, goal_miles - actual_miles)
        percentage = (actual_miles / goal_miles * 100) if goal_miles > 0 else 0
        
        # Return EVERYTHING
        return {
            "goal_miles": goal_miles,
            "actual_miles": round(actual_miles, 2),
            "actual_meters": total_distance_meters,  # For backward compatibility
            "goal_met": goal_met,
            "remaining_miles": round(remaining_miles, 2),
            "percentage": round(percentage, 1),
            "activities_count": len([a for a in activities if a.get("type") == "Run"])
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Strava API error: {str(e)}")

@app.put("/update-goal")
async def update_goal(goal: Goal, session_id: str = Cookie(None)): 
    #Validation
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = sessions.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    if goal.updated_goal <= 0:
        raise HTTPException(status_code=400, detail="Goal must be positive")
    
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.strava_user_id== session["user_info"]["id"]).first()
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        user.weekly_goal_miles = goal.updated_goal
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return await check_goal(session_id)
        
