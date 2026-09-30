from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from .config import settings
from .database import Base, engine, get_db
from .models import User, Event, RSVP, Announcement, Notification, Waitlist
from .schemas import RegisterIn, LoginIn, TokenOut, EventIn, EventOut, RSVPIn, RSVPOut, AnnouncementIn
from .security import hash_password, verify_password, create_token, current_user, require_role
from .services import upsert_rsvp, counts, ensure_event_owner
from .realtime import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Cloud Event RSVP Tracker", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "environment": settings.app_env}

@app.post("/api/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    role = data.role.upper()
    if role not in {"ATTENDEE", "ORGANIZER"}:
        role = "ATTENDEE"
    if db.query(User).filter_by(email=data.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    user = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user), "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@app.post("/api/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user), "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@app.post("/api/logout")
def logout(user: User = Depends(current_user)):
    return {"message": "Logout is client-side for JWT mode; discard the token."}

@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@app.post("/api/events", response_model=EventOut)
def create_event(data: EventIn, user: User = Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    if data.start_time >= data.end_time:
        raise HTTPException(422, "End time must be after start time")
    if data.registration_deadline > data.event_date:
        raise HTTPException(422, "Registration deadline cannot be after event date")
    event = Event(organizer_id=user.id, **data.model_dump())
    db.add(event); db.commit(); db.refresh(event)
    return event

@app.get("/api/events", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.asc(), Event.start_time.asc()).all()

@app.get("/api/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    return event

@app.put("/api/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, data: EventIn, user: User = Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    ensure_event_owner(event, user.id)
    for key, value in data.model_dump().items():
        setattr(event, key, value)
    db.commit(); db.refresh(event)
    return event

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, user: User = Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    ensure_event_owner(event, user.id)
    event.status = "CANCELLED"
    db.commit()
    users = db.query(RSVP.user_id).filter_by(event_id=event_id).all()
    for (uid,) in users:
        db.add(Notification(user_id=uid, event_id=event_id, type="CANCELLED",
                             message=f"{event.event_name} has been cancelled."))
    db.commit()
    return {"message": "Event cancelled"}

@app.post("/api/events/{event_id}/rsvp", response_model=RSVPOut)
async def create_rsvp(event_id: int, data: RSVPIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    try:
        rsvp = upsert_rsvp(db, event, user.id, data.status)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate RSVP request")
    await manager.broadcast(event_id, {"type": "RSVP_UPDATED", "event_id": event_id, "counts": counts(db, event_id)})
    return rsvp

@app.put("/api/events/{event_id}/rsvp", response_model=RSVPOut)
async def update_rsvp(event_id: int, data: RSVPIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return await create_rsvp(event_id, data, user, db)

@app.delete("/api/events/{event_id}/rsvp")
async def delete_rsvp(event_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rsvp = db.query(RSVP).filter_by(event_id=event_id, user_id=user.id).first()
    if not rsvp: raise HTTPException(404, "RSVP not found")
    old = rsvp.status
    db.delete(rsvp); db.commit()
    if old == "GOING":
        from .services import promote_waitlisted
        event = db.get(Event, event_id)
        if event: promote_waitlisted(db, event)
    await manager.broadcast(event_id, {"type": "RSVP_UPDATED", "event_id": event_id, "counts": counts(db, event_id)})
    return {"message": "RSVP cancelled"}

@app.get("/api/rsvps/me")
def my_rsvps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(RSVP).filter_by(user_id=user.id).all()

@app.get("/api/events/{event_id}/rsvps")
def event_rsvps(event_id: int, user: User = Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    ensure_event_owner(event, user.id)
    return db.query(RSVP).filter_by(event_id=event_id).all()

@app.get("/api/events/{event_id}/analytics")
def analytics(event_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    c = counts(db, event_id)
    responded = c["GOING"] + c["MAYBE"] + c["NOT_GOING"]
    invitees = responded
    response_rate = round((responded / invitees) * 100, 2) if invitees else 0
    utilization = round((c["GOING"] / c["capacity"]) * 100, 2) if c["capacity"] else 0
    waitlist = db.query(Waitlist).filter_by(event_id=event_id, status="WAITLISTED").count()
    return {"event_id": event_id, **c, "responded": responded, "response_rate": response_rate,
            "capacity_utilization": utilization, "waitlist_size": waitlist}

@app.post("/api/events/{event_id}/announcements")
def announcement(event_id: int, data: AnnouncementIn, user: User = Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    ensure_event_owner(event, user.id)
    a = Announcement(event_id=event_id, title=data.title, message=data.message)
    db.add(a)
    users = db.query(RSVP.user_id).filter_by(event_id=event_id).all()
    for (uid,) in users:
        db.add(Notification(user_id=uid, event_id=event_id, type="ANNOUNCEMENT",
                             message=f"{data.title}: {data.message}"))
    db.commit(); db.refresh(a)
    return a

@app.get("/api/events/{event_id}/announcements")
def announcements(event_id: int, db: Session = Depends(get_db)):
    return db.query(Announcement).filter_by(event_id=event_id).order_by(Announcement.created_at.desc()).all()

@app.get("/api/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()

@app.put("/api/notifications/{notification_id}/read")
def mark_read(notification_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notification_id)
    if not n or n.user_id != user.id: raise HTTPException(404, "Notification not found")
    n.read = True; db.commit()
    return {"message": "marked read"}

@app.get("/api/events/{event_id}/counts")
def event_counts(event_id: int, db: Session = Depends(get_db)):
    if not db.get(Event, event_id): raise HTTPException(404, "Event not found")
    return counts(db, event_id)

@app.websocket("/ws/events/{event_id}")
async def websocket_endpoint(websocket: WebSocket, event_id: int):
    await manager.connect(event_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(event_id, websocket)
    except Exception:
        manager.disconnect(event_id, websocket)
