# Architecture

## Local classroom mode

Browser → React/Vite → FastAPI REST API → SQLAlchemy → SQLite
                           ↘ WebSocket ConnectionManager → connected browsers

## Recommended student cloud mode

Browser → Vercel static frontend
       → FastAPI on Render
       → Supabase PostgreSQL
       → Supabase Auth (optional managed-auth upgrade)
       → Supabase Realtime for database change subscriptions

The repository keeps a local WebSocket path because it makes the real-time behavior
easy to demonstrate and test without paid infrastructure.

## Event flow

Organizer → POST /api/events → database → event appears in GET /api/events

Attendee → POST /api/events/{id}/rsvp
         → backend validates auth, deadline, duplicate record and capacity
         → database transaction
         → WebSocket broadcast
         → organizer dashboard updates without refresh

## Scaling

At higher scale, replace the in-process WebSocket manager with a managed realtime
layer such as Supabase Realtime/Broadcast or AWS API Gateway WebSocket API.
