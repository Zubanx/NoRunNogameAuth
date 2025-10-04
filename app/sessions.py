from datetime import datetime
from typing import Optional, Dict
import secrets
from fastapi import HTTPException
from database import SessionLocal
from models_db import Session, User


def create_session(user_info: dict, strava_access_token: str, 
                   strava_refresh_token: str, expires_at: datetime) -> str:
    session_id = secrets.token_urlsafe(32)
    db = SessionLocal()
    try:
        strava_user_id = user_info["id"]
        user = db.query(User).filter(User.strava_user_id == strava_user_id).first()
        if not user:
            # User doesn't exist, create them
            user = User(
            strava_user_id=strava_user_id,
            firstname=user_info.get("firstname"),
            lastname=user_info.get("lastname"),
            weekly_goal_miles=15.0  # Default goal
            )
            db.add(user)

        db_session = Session(session_id=session_id, strava_user_id=strava_user_id, strava_access_token=strava_access_token, strava_refresh_token=strava_refresh_token, expires_at=expires_at)
        db.add(db_session)

        db.commit()

        return session_id
    
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_session(session_id: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        if not session:
            return None
        user = db.query(User).filter(User.strava_user_id == session.strava_user_id).first()
        if not user:
            return None
        user_data = {
            "user_info": {
                "id": user.strava_user_id,
                "firstname" : user.firstname,
                "lastname" : user.lastname,

            },
            "strava_access_token" : session.strava_access_token,
            "strava_refresh_token" : session.strava_refresh_token,
            "expires_at" : session.expires_at,
            "weekly_goal_miles" : user.weekly_goal_miles
        }
        return user_data

    finally:
        db.close()

def delete_session(session_id: str) -> bool:
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.session_id  == session_id).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
    

def update_session_tokens(session_id: str, access_token: str, 
                         refresh_token: str, expires_at: datetime) -> bool:
    
    db = SessionLocal()

    try:
        session = db.query(Session).filter(Session.session_id  == session_id).first()
        if not session:
            return False
        session.strava_access_token = access_token
        session.strava_refresh_token = refresh_token
        session.expires_at = expires_at
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    