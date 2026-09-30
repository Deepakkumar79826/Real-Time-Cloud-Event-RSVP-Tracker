const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, {...options, headers});
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || "Request failed");
  return body;
}
export const api = {
  register: (data) => request("/api/register", {method:"POST", body:JSON.stringify(data)}),
  login: (data) => request("/api/login", {method:"POST", body:JSON.stringify(data)}),
  me: () => request("/api/me"),
  events: () => request("/api/events"),
  createEvent: (data) => request("/api/events", {method:"POST", body:JSON.stringify(data)}),
  updateEvent: (id,data) => request(`/api/events/${id}`, {method:"PUT", body:JSON.stringify(data)}),
  cancelEvent: (id) => request(`/api/events/${id}`, {method:"DELETE"}),
  counts: (id) => request(`/api/events/${id}/counts`),
  analytics: (id) => request(`/api/events/${id}/analytics`),
  rsvp: (id,status) => request(`/api/events/${id}/rsvp`, {method:"POST", body:JSON.stringify({status})}),
  cancelRsvp: (id) => request(`/api/events/${id}/rsvp`, {method:"DELETE"}),
  myRsvps: () => request("/api/rsvps/me"),
  announcement: (id,data) => request(`/api/events/${id}/announcements`, {method:"POST", body:JSON.stringify(data)}),
  announcements: (id) => request(`/api/events/${id}/announcements`),
  notifications: () => request("/api/notifications"),
};
export { API };
