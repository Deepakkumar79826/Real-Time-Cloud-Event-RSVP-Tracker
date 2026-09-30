# Cloud Concepts Mapped to the Project

| Concept | Where demonstrated |
|---|---|
| Cloud Computing | Remote frontend/API/database |
| SaaS | Finished event platform accessed through browser |
| PaaS | Vercel/Render managed deployment |
| IaaS | AWS EC2/ECS alternative |
| Cloud Database | Supabase PostgreSQL |
| Realtime DB | Supabase Realtime |
| Authentication | JWT locally; Supabase Auth cloud option |
| Authorization | RBAC + owner checks + optional RLS |
| REST API | FastAPI `/api/*` endpoints |
| WebSockets | `/ws/events/{id}` |
| SSE | Alternative design, not primary implementation |
| Serverless | AWS Lambda alternative |
| Event-driven architecture | RSVP → notification/realtime event |
| Cloud Functions | Optional notification/event functions |
| Scalability | Stateless API + managed DB + realtime layer |
| Elasticity | Autoscaling/serverless cloud alternative |
| High availability | Managed multi-node services / replicas |
| Load balancing | Cloud provider frontend/API routing |
| API Gateway | AWS API Gateway alternative |
| CDN | Vercel/CloudFront |
| Caching | Redis/CDN for popular event reads |
| Environment variables | `.env` + deployment secrets |
| Secrets management | Provider secret store |
| Logging | Render/provider logs + application errors |
| Monitoring | Cloud metrics and health endpoint |
| Backup | Managed PostgreSQL backup strategy |
| CI/CD | GitHub → Vercel/Render automatic deployments |
| Security | TLS, hashing, JWT, RBAC, RLS, validation |
