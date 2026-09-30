from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "ATTENDEE"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class EventIn(BaseModel):
    event_name: str
    description: str = ""
    event_type: str = "Workshop"
    event_date: str
    start_time: str
    end_time: str
    venue: str = ""
    online_link: str | None = None
    maximum_capacity: int = Field(gt=0)
    registration_deadline: str
    status: str = "PUBLISHED"

class EventOut(EventIn):
    id: int
    organizer_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RSVPIn(BaseModel):
    status: str

class AnnouncementIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=1)

class RSVPOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)
