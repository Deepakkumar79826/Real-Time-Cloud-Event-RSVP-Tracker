# Real-Time Cloud-Based Event Planning & RSVP Tracker

A cloud-oriented event platform demonstrating **Cloud Computing, REST APIs, authentication,
RBAC, real-time communication, capacity control, notifications, analytics, testing and
cloud deployment**.

## Architecture

```text
                  ┌──────────────────────┐
                  │      Browser(s)      │
                  │ React + Vite         │
                  └──────────┬───────────┘
                             │ HTTPS / WebSocket
                  ┌──────────▼───────────┐
                  │ FastAPI REST API     │
                  │ Auth + RBAC + Logic  │
                  └───────┬───────┬──────┘
                          │       │
                    SQLAlchemy    │ WebSocket
                          │       │
                  ┌───────▼───┐   │
                  │ PostgreSQL │   │
                  │ / SQLite   │   │
                  └────────────┘   │
                                   ▼
                         Live Dashboard Updates
```

## Features

- Organizer and attendee roles
- Event CRUD/cancellation
- Going / Maybe / Not Going
- Unique `(event_id,user_id)` RSVP
- Capacity enforcement
- FIFO waitlist
- Announcements
- In-app notifications
- Organizer analytics
- WebSocket real-time counters
- JWT authentication
- RBAC and ownership checks
- Automated API tests
- Docker deployment
- Supabase PostgreSQL migration schema

## Recommended student cloud stack

**Frontend:** Vercel Hobby  
**Backend:** Render Free web service  
**Database + optional managed Auth + Realtime:** Supabase Free plan

These services currently provide free/student-friendly entry points, but free plans have
quotas/limitations and should not be treated as production guarantees.

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open `http://localhost:5173`.

Demo accounts:

- Organizer: `organizer@example.com` / `Organizer123!`
- Attendee: `attendee@example.com` / `Attendee123!`

## Real-Time Demo

1. Open browser A and login as organizer.
2. Open browser B and login as attendee.
3. Select the same event.
4. Browser B selects GOING.
5. Browser A's count changes without refresh.
6. Open browser C as another attendee and repeat.
7. Change GOING → MAYBE and observe the live counter.

## Cloud Deployment

### Supabase

1. Create a free Supabase project.
2. Open SQL Editor.
3. Run `cloud/supabase_schema.sql`.
4. Enable Realtime for the required tables.
5. Store database connection string as `DATABASE_URL`.
6. Store a strong `JWT_SECRET` as a deployment secret.

### Render

Create a Web Service from the repository:
- Root directory: `backend`
- Docker deployment
- Environment variables:
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `CORS_ORIGINS`
  - `APP_ENV=cloud`

### Vercel

Import `frontend/`, set:
- `VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com`

Build command:
`npm run build`

Output:
`dist`

## Cloud Authentication

The included runnable mode uses FastAPI JWT authentication so the project works locally
without a third-party account. For the managed cloud version, Supabase Auth can replace
the local password/JWT layer. Supabase Auth supports password authentication and JWT-based
authorization, and its database integrates with RLS.

## Important Concurrency Note

The SQLite local implementation demonstrates the logic and unique constraint. For real
production concurrency, use PostgreSQL and perform the capacity check and RSVP mutation
inside one transaction using row locking or an atomic conditional update. Never trust a
frontend counter.

## API

See `docs/API.md`.

## Testing

```bash
pytest -q
```

## GitHub Topics

`cloud-computing`, `event-management`, `rsvp`, `realtime`, `python`, `fastapi`,
`react`, `websocket`, `postgresql`, `rest-api`, `serverless`, `authentication`

## Suggested Commit History

1. Create cloud event platform architecture
2. Implement authentication and roles
3. Add event management module
4. Implement RSVP workflow
5. Integrate cloud database
6. Add real-time RSVP updates
7. Implement capacity-safe transactions
8. Add optional waitlist
9. Build organizer dashboard
10. Add announcements and notifications
11. Implement event analytics
12. Add security controls
13. Add automated tests
14. Deploy application to cloud
15. Complete README and documentation

## Limitations

The local WebSocket manager is process-local. For horizontal scaling use Supabase Realtime,
Redis pub/sub, or a managed WebSocket service.

## Author

Deepak Kumar
