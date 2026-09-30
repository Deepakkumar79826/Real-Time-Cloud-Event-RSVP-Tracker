# Test Plan

| ID | Scenario | Expected |
|---|---|---|
| T01 | Registration | User created |
| T02 | Duplicate registration | 409 |
| T03 | Login | JWT returned |
| T04 | Organizer creates event | 200 |
| T05 | Attendee creates event | 403 |
| T06 | Event retrieval | Event returned |
| T07 | Valid RSVP | RSVP stored |
| T08 | Duplicate RSVP | Existing record updated |
| T09 | MAYBE → GOING | Counts change |
| T10 | Cancel RSVP | RSVP removed |
| T11 | Past deadline | 409 |
| T12 | Full event | GOING rejected/waitlisted |
| T13 | Unauthorized event edit | 403 |
| T14 | Unauthorized RSVP access | 403 |
| T15 | Announcement | Notification generated |
| T16 | Realtime | Connected dashboard receives event |
| T17 | Analytics | Counts and percentages correct |
| T18 | Invalid token | 401 |
| T19 | Event cancellation | Notifications generated |
| T20 | Database outage | Graceful 5xx + logs |
| T21 | WebSocket outage | UI can reconnect/refresh |
| T22 | Duplicate request | Unique constraint prevents duplicate |
| T23 | Concurrent final seat | Production DB must use transaction/conditional write |
| T24 | Token expiry | 401 |
| T25 | Waitlist promotion | FIFO candidate promoted |
