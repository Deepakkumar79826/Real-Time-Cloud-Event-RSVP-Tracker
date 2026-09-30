# Interview Preparation

## 1. Explain your project.
I built a Real-Time Cloud-Based Event Planning and RSVP Tracker. Organizers can create and
manage events, while attendees can RSVP with Going, Maybe or Not Going. The backend is a
FastAPI REST service, event data is stored centrally, and WebSockets push RSVP count changes
to connected dashboards without a page refresh. I also implemented JWT authentication,
role-based authorization, capacity checks, waitlist behavior, announcements, notifications,
analytics and automated tests.

## 2. Why is this a cloud computing project?
The application is designed as a distributed, remotely accessible service. The frontend,
API and managed database can run on separate cloud services. Cloud hosting provides shared
access, managed storage, scalable compute, centralized data and deployment automation.

## 3. What does real-time mean here?
It means a connected dashboard receives an RSVP change immediately after the backend accepts
it. In the local implementation this is done through WebSockets. In a cloud deployment it
can be replaced by Supabase Realtime or a managed WebSocket service.

## 4. Why not let the frontend update the count?
Because the frontend is untrusted. The backend/database is the source of truth. A user could
otherwise manipulate browser JavaScript and display fake attendance numbers.

## 5. How do you prevent duplicate RSVPs?
The database has a unique constraint on `(event_id, user_id)`. The API also performs an
upsert-style operation so a second RSVP changes the existing response instead of creating
another active record.

## 6. How do you handle capacity?
Before accepting GOING, the backend checks the current GOING count against the event
capacity. At production scale the check and mutation must be inside one database transaction
with a locking or atomic conditional-write strategy to prevent two final-seat requests from
both succeeding.

## 7. What is the difference between authentication and authorization?
Authentication answers “Who are you?” Authorization answers “What are you allowed to do?”
The project uses login/JWT for authentication and role plus event-owner checks for
authorization.

## 8. How would you scale this to one million users?
I would put the frontend behind a CDN, use autoscaling/serverless API compute, managed
PostgreSQL with proper indexes and connection pooling, caching for read-heavy endpoints,
queues for notifications, rate limiting, and a horizontally scalable realtime service.
I would also monitor latency, database load and WebSocket connection counts.

## 9. What happens if WebSocket disconnects?
The application can reconnect or fall back to fetching `/api/events/{id}/counts`. The
database remains the source of truth, so losing a WebSocket connection does not lose the RSVP.

## 10. How did you secure the application?
Passwords are hashed, JWTs are used for protected APIs, roles are checked server-side,
organizers can modify only their own events, input is validated, secrets are environment
variables, CORS is configured, and database constraints enforce integrity. In production
I would add HTTPS, RLS, rate limiting, centralized secrets management and audit logging.
