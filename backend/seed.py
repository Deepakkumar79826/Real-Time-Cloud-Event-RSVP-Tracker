from app.database import Base, engine, SessionLocal
from app.models import User, Event
from app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(User).filter_by(email="organizer@example.com").first():
    organizer = User(name="Demo Organizer", email="organizer@example.com",
                     password_hash=hash_password("Organizer123!"), role="ORGANIZER")
    attendee = User(name="Demo Attendee", email="attendee@example.com",
                    password_hash=hash_password("Attendee123!"), role="ATTENDEE")
    db.add_all([organizer, attendee]); db.commit(); db.refresh(organizer)
    event = Event(
        organizer_id=organizer.id,
        event_name="Cloud Computing Workshop",
        description="Synthetic demonstration event for the cloud computing project.",
        event_type="Workshop",
        event_date="2026-12-15",
        start_time="10:00",
        end_time="13:00",
        venue="Virtual Lab",
        online_link="https://example.com/meeting",
        maximum_capacity=100,
        registration_deadline="2026-12-14",
        status="PUBLISHED"
    )
    db.add(event); db.commit()
    print("Seeded organizer@example.com / Organizer123! and attendee@example.com / Attendee123!")
else:
    print("Seed data already exists.")
db.close()
