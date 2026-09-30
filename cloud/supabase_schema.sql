-- Cloud PostgreSQL schema. Use this when migrating from local SQLite.
-- For production, prefer Supabase Auth + RLS policies; the local FastAPI JWT mode
-- remains available for offline classroom demonstrations.

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null,
  role text not null default 'ATTENDEE' check (role in ('ATTENDEE','ORGANIZER','ADMIN')),
  created_at timestamptz default now()
);

create table if not exists events (
  id bigint generated always as identity primary key,
  organizer_id uuid not null references profiles(id),
  event_name text not null,
  description text default '',
  event_type text default 'Workshop',
  event_date date not null,
  start_time time not null,
  end_time time not null,
  venue text default '',
  online_link text,
  maximum_capacity integer not null check (maximum_capacity > 0),
  registration_deadline date not null,
  status text not null default 'DRAFT'
    check (status in ('DRAFT','PUBLISHED','FULL','COMPLETED','CANCELLED')),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  check (end_time > start_time),
  check (registration_deadline <= event_date)
);

create table if not exists rsvps (
  id bigint generated always as identity primary key,
  event_id bigint not null references events(id) on delete cascade,
  user_id uuid not null references profiles(id) on delete cascade,
  status text not null check (status in ('GOING','MAYBE','NOT_GOING')),
  responded_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(event_id,user_id)
);

create index if not exists idx_rsvps_event_status on rsvps(event_id,status);
create index if not exists idx_events_date on events(event_date,status);

create table if not exists announcements (
  id bigint generated always as identity primary key,
  event_id bigint not null references events(id) on delete cascade,
  title text not null,
  message text not null,
  created_at timestamptz default now()
);

create table if not exists notifications (
  id bigint generated always as identity primary key,
  user_id uuid not null references profiles(id) on delete cascade,
  event_id bigint references events(id) on delete cascade,
  type text not null,
  message text not null,
  read boolean default false,
  created_at timestamptz default now()
);

create table if not exists waitlist (
  id bigint generated always as identity primary key,
  event_id bigint not null references events(id) on delete cascade,
  user_id uuid not null references profiles(id) on delete cascade,
  joined_at timestamptz default now(),
  status text not null default 'WAITLISTED',
  unique(event_id,user_id)
);

-- Enable realtime for the tables needed by the dashboard.
alter publication supabase_realtime add table rsvps;
alter publication supabase_realtime add table announcements;
alter publication supabase_realtime add table notifications;

-- Production note:
-- Add RLS policies before exposing tables to browser clients.
