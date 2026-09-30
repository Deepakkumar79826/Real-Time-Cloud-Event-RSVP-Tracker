from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Event, RSVP, Announcement, Notification, Waitlist

VALID_RSVP = {"GOING", "MAYBE", "NOT_GOING"}

def counts(db: Session, event_id: int):
    rows = db.query(RSVP.status, func.count(RSVP.id)).filter(RSVP.event_id == event_id).group_by(RSVP.status).all()
    data = {"GOING": 0, "MAYBE": 0, "NOT_GOING": 0}
    for status, count in rows:
        data[status] = count
    event = db.get(Event, event_id)
    return {
        **data,
        "capacity": event.maximum_capacity if event else 0,
        "available": max((event.maximum_capacity if event else 0) - data["GOING"], 0)
    }

def ensure_event_owner(event: Event, user_id: int):
    if event.organizer_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own this event")

def upsert_rsvp(db: Session, event: Event, user_id: int, status: str):
    """Create/update an RSVP.

    PostgreSQL production mode locks the event row before checking capacity.
    That makes the critical check + write serial for one event, preventing two
    simultaneous final-seat requests from both passing the capacity test.
    SQLite remains the portable classroom mode.
    """
    status = status.upper()
    if status not in VALID_RSVP:
        raise HTTPException(status_code=422, detail="Invalid RSVP status")
    if event.status in {"CANCELLED", "COMPLETED"}:
        raise HTTPException(status_code=409, detail="Event is not accepting RSVPs")
    if datetime.utcnow().date().isoformat() > event.registration_deadline:
        raise HTTPException(status_code=409, detail="Registration deadline has passed")

    is_postgres = db.bind.dialect.name == "postgresql"
    if is_postgres:
        event = db.query(Event).filter(Event.id == event.id).with_for_update().one()

    existing = db.query(RSVP).filter_by(event_id=event.id, user_id=user_id).first()
    current_going = db.query(RSVP).filter_by(event_id=event.id, status="GOING").count()

    if status == "GOING" and (not existing or existing.status != "GOING") and current_going >= event.maximum_capacity:
        wait = db.query(Waitlist).filter_by(event_id=event.id, user_id=user_id).first()
        if not wait:
            wait = Waitlist(event_id=event.id, user_id=user_id)
            db.add(wait)
            db.add(Notification(user_id=user_id, event_id=event.id, type="WAITLISTED",
                                message=f"You were added to the waitlist for {event.event_name}."))
            db.commit()
        raise HTTPException(status_code=409, detail="Event is full. You were added to the waitlist.")

    if existing:
        old = existing.status
        existing.status = status
        existing.updated_at = datetime.utcnow()
        rsvp = existing
    else:
        old = None
        rsvp = RSVP(event_id=event.id, user_id=user_id, status=status)
        db.add(rsvp)

    db.add(Notification(user_id=user_id, event_id=event.id, type="RSVP",
                         message=f"Your RSVP for {event.event_name} is {status}."))
    db.commit()
    db.refresh(rsvp)

    if old == "GOING" and status != "GOING":
        promote_waitlisted(db, event)
    return rsvp

def promote_waitlisted(db: Session, event: Event):
    going = db.query(RSVP).filter_by(event_id=event.id, status="GOING").count()
    if going >= event.maximum_capacity:
        return
    candidate = (db.query(Waitlist)
                 .filter_by(event_id=event.id, status="WAITLISTED")
                 .order_by(Waitlist.joined_at.asc())
                 .first())
    if candidate:
        rsvp = db.query(RSVP).filter_by(event_id=event.id, user_id=candidate.user_id).first()
        if rsvp:
            rsvp.status = "GOING"
        else:
            db.add(RSVP(event_id=event.id, user_id=candidate.user_id, status="GOING"))
        candidate.status = "PROMOTED"
        db.add(Notification(user_id=candidate.user_id, event_id=event.id, type="WAITLIST_PROMOTED",
                             message=f"A seat opened for {event.event_name}; you were promoted from the waitlist."))
        db.commit()
