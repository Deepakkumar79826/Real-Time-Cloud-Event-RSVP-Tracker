# Project Report

## Abstract
The Real-Time Cloud-Based Event Planning & RSVP Tracker is a cloud-oriented application
for creating events, collecting RSVP responses, tracking capacity, sending announcements,
and presenting live analytics. The system demonstrates cloud-hosted APIs, managed database
concepts, authentication, authorization, real-time communication, notifications,
scalability and failure handling.

## Problem Statement
Manual RSVP spreadsheets become difficult to coordinate when attendance changes frequently.
Organizers need a central source of truth and live visibility.

## Objectives
- Centralized event management
- Secure authentication and role-based authorization
- Real-time RSVP visibility
- Capacity-safe registration
- Notifications and announcements
- Analytics
- Cloud deployment readiness

## Existing System
Manual forms, spreadsheets, email chains and static event pages.

## Proposed System
A browser-based, API-driven system with centralized database storage and real-time updates.

## Cloud Computing Concepts
SaaS: the finished event application.
PaaS: Vercel/Render-style managed deployment.
Cloud database: Supabase PostgreSQL.
Serverless concept: Lambda/API Gateway equivalent for advanced deployment.
CDN: Vercel/CloudFront delivery.
API gateway: API Gateway or managed reverse proxy in enterprise architecture.
Caching: optional Redis/CDN caching for read-heavy event lists.
Secrets: environment variables/secret stores.
Monitoring: provider logs and metrics.

## Real-Time Computing
Local mode uses WebSockets. Cloud mode can use Supabase Realtime database subscriptions.

## Database Design
Users, events, RSVPs, announcements, notifications and waitlist are separate logical entities.

## Concurrency
A naive read-then-insert capacity check is race-prone. Production PostgreSQL should perform
the capacity check and RSVP mutation inside a transaction with a locking/conditional-update
strategy. SQLite is used for classroom portability, not high-concurrency production.

## Security
JWT authentication, password hashing, RBAC, owner checks, input validation, CORS,
environment variables and database constraints are included.

## Scalability
For large traffic, use load balancing, autoscaling/serverless compute, managed PostgreSQL,
Redis/cache, queues, CDN and a horizontally scalable realtime service.

## Failure Handling
The application returns structured errors, uses database constraints for idempotency,
and the browser can recover through refresh/reconnect. Production deployments should add
retry policies, circuit breakers, observability and durable queues.

## Results
The project demonstrates event CRUD, RSVP lifecycle, live counters, notifications,
analytics and deployment-ready architecture.

## Limitations
The local WebSocket manager is process-local. High-scale deployments require a managed
realtime layer. Email/SMS are intentionally optional to avoid paid services.

## Future Scope
Waitlist automation, QR check-in, email/push notifications, calendar integration,
Redis caching, background jobs, distributed tracing and infrastructure-as-code.
