from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from database import Base
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import TIMESTAMP

class User(Base):
    #Stores user preferences (goals, etc) - persists across sessions
    __tablename__ ="users"

    id = Column(Integer, primary_key=True, index=True)
    strava_user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    weekly_goal_miles = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))


class Session(Base):
    #Stores active sessions with tokens - temporary
    __tablename__ ="sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    strava_user_id = Column(BigInteger, nullable=False)
    strava_access_token = Column(String, nullable=False)
    strava_refresh_token = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, )
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))