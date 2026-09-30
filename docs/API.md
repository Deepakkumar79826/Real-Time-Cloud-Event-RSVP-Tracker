# API Reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | /api/register | No | Register |
| POST | /api/login | No | Login |
| POST | /api/logout | Yes | Client token logout |
| GET | /api/me | Yes | Current user |
| POST | /api/events | Organizer | Create event |
| GET | /api/events | No | List events |
| GET | /api/events/{id} | No | Event details |
| PUT | /api/events/{id} | Organizer owner | Update event |
| DELETE | /api/events/{id} | Organizer owner | Cancel event |
| POST | /api/events/{id}/rsvp | Yes | Create/update RSVP |
| PUT | /api/events/{id}/rsvp | Yes | Update RSVP |
| DELETE | /api/events/{id}/rsvp | Yes | Cancel RSVP |
| GET | /api/rsvps/me | Yes | Own RSVPs |
| GET | /api/events/{id}/rsvps | Organizer owner | Attendee list |
| GET | /api/events/{id}/analytics | Yes | Analytics |
| POST | /api/events/{id}/announcements | Organizer owner | Announcement |
| GET | /api/events/{id}/announcements | No | Announcements |
| GET | /api/notifications | Yes | Notifications |
| PUT | /api/notifications/{id}/read | Yes | Mark read |
| GET | /api/events/{id}/counts | No | Live counts |
| WS | /ws/events/{id} | Demo | Real-time event room |

Common status codes: 200/201 success, 400 validation, 401 unauthenticated,
403 forbidden, 404 not found, 409 conflict/capacity, 422 invalid input, 500 server error.
