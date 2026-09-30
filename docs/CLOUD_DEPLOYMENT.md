# Cloud Deployment Guide

## A. Student-friendly architecture

```text
Users
  |
  v
Vercel CDN / Static Hosting
  |
  v
React Frontend
  |
  | HTTPS
  v
Render FastAPI
  |
  +------> Supabase PostgreSQL
  |
  +------> Supabase Auth (optional managed auth)
  |
  +------> Supabase Realtime (cloud realtime)
```

### Supabase

1. Create project.
2. Copy the PostgreSQL connection string.
3. Run `cloud/supabase_schema.sql`.
4. Add Realtime publication tables.
5. Keep service-role keys out of the browser.
6. For browser-direct access, enable RLS and write least-privilege policies.

### Render

Use Dockerfile in `backend/`.
Set:
- `DATABASE_URL`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `APP_ENV=cloud`

### Vercel

Deploy `frontend/`.
Set `VITE_API_URL` to the Render API URL.

## B. AWS enterprise architecture

```text
CloudFront
   |
S3/Next.js Frontend
   |
API Gateway
   |
Lambda / ECS
   |
RDS PostgreSQL or DynamoDB
   |
SQS -> Lambda -> SNS/SES
   |
API Gateway WebSocket
   |
CloudWatch
```

AWS API Gateway WebSocket APIs are bidirectional and can integrate with Lambda and other
AWS services. Use Cognito for managed identity in a full AWS implementation.

## Azure equivalent

Azure Front Door/CDN → Static Web Apps → API Management → Functions/Container Apps →
Azure Database for PostgreSQL/Cosmos DB → Service Bus → Notification Hubs → Application Insights.

## GCP equivalent

Cloud CDN → Cloud Storage/Firebase Hosting → API Gateway/Cloud Run → Cloud SQL/Firestore →
Pub/Sub → Cloud Monitoring.

## Free-tier caveat

Free tiers change over time and have quotas. Verify current limits before deployment.
The repository therefore always keeps a local execution path.
