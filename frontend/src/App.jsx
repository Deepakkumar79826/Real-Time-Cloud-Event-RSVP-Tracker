import React, {useEffect, useMemo, useState} from "react";
import {api, API} from "./api";
import {BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, ResponsiveContainer} from "recharts";

const emptyEvent = {event_name:"",description:"",event_type:"Workshop",event_date:"2026-12-15",
 start_time:"10:00",end_time:"13:00",venue:"Virtual Lab",online_link:"",
 maximum_capacity:100,registration_deadline:"2026-12-14",status:"PUBLISHED"};

function App(){
  const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem("user")||"null"));
  const [events,setEvents]=useState([]);
  const [selected,setSelected]=useState(null);
  const [counts,setCounts]=useState(null);
  const [rsvps,setRsvps]=useState([]);
  const [notifications,setNotifications]=useState([]);
  const [form,setForm]=useState(emptyEvent);
  const [auth,setAuth]=useState({mode:"login",name:"",email:"",password:"",role:"ATTENDEE"});
  const [error,setError]=useState("");

  async function load(){
    try{
      setEvents(await api.events());
      if(user) setNotifications(await api.notifications());
    }catch(e){setError(e.message)}
  }
  useEffect(()=>{load()},[user]);

  useEffect(()=>{
    if(!selected) return;
    api.counts(selected.id).then(setCounts).catch(()=>{});
    const ws = new WebSocket(`${API.replace(/^http/,"ws")}/ws/events/${selected.id}`);
    ws.onopen=()=>ws.send("subscribe");
    ws.onmessage=(e)=>{const msg=JSON.parse(e.data); if(msg.counts) setCounts(msg.counts)};
    ws.onerror=()=>{};
    return ()=>ws.close();
  },[selected]);

  const selectedRsvp = useMemo(()=>rsvps.find(r=>r.event_id===selected?.id)?.status,null);

  async function submitAuth(e){
    e.preventDefault(); setError("");
    try{
      const data = auth.mode==="login" ? await api.login({email:auth.email,password:auth.password})
        : await api.register(auth);
      localStorage.setItem("token",data.access_token); localStorage.setItem("user",JSON.stringify(data.user));
      setUser(data.user); setAuth({...auth,password:""});
    }catch(e){setError(e.message)}
  }

  async function doRsvp(status){
    try{
      await api.rsvp(selected.id,status);
      setRsvps(await api.myRsvps());
      setNotifications(await api.notifications());
      setError("");
    }catch(e){setError(e.message)}
  }

  async function createEvent(e){
    e.preventDefault();
    try{await api.createEvent({...form,maximum_capacity:Number(form.maximum_capacity)});
      setForm(emptyEvent); await load(); setError("");
    }catch(e){setError(e.message)}
  }

  function logout(){
    localStorage.removeItem("token"); localStorage.removeItem("user"); setUser(null); setSelected(null);
  }

  if(!user) return <Auth auth={auth} setAuth={setAuth} submitAuth={submitAuth} error={error}/>;

  return <div className="app">
    <header><div><h1>☁️ Cloud Event RSVP</h1><small>Real-time cloud computing reference project</small></div>
      <div className="userbar">{user.name} · <b>{user.role}</b><button onClick={logout}>Logout</button></div>
    </header>
    <main>
      {error && <div className="alert">{error}</div>}
      <section className="hero">
        <div><h2>Live Event Operations</h2><p>RSVP changes are pushed to connected dashboards over WebSockets.</p></div>
        <span className="live">● LIVE</span>
      </section>

      <div className="grid">
        <section className="card">
          <h2>Events</h2>
          {events.map(ev=><div key={ev.id} className={`event ${selected?.id===ev.id?"active":""}`} onClick={async()=>{setSelected(ev);setRsvps(await api.myRsvps())}}>
            <div><strong>{ev.event_name}</strong><span className="badge">{ev.status}</span></div>
            <small>{ev.event_date} · {ev.start_time}-{ev.end_time} · {ev.venue}</small>
          </div>)}
        </section>

        <section className="card">
          {selected ? <EventPanel event={selected} counts={counts} selectedRsvp={selectedRsvp} doRsvp={doRsvp}
             user={user} notifications={notifications} setNotifications={setNotifications} reload={load}/> :
             <div className="empty"><h2>Select an event</h2><p>Open this app in multiple browser windows to demonstrate live RSVP updates.</p></div>}
        </section>
      </div>

      {user.role==="ORGANIZER" && <section className="card organizer">
        <h2>Organizer Console</h2>
        <form onSubmit={createEvent} className="event-form">
          {Object.keys(emptyEvent).map(k=>k==="status"?null:<label key={k}>{k.replaceAll("_"," ")}
            <input value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})} type={k.includes("capacity")?"number":k.includes("date")?"date":k.includes("time")?"time":"text"} required={["event_name","event_date","start_time","end_time","maximum_capacity","registration_deadline"].includes(k)}/>
          </label>)}
          <button>Create Event</button>
        </form>
      </section>}

      <section className="card">
        <h2>Notifications</h2>
        {notifications.length===0?<p>No notifications yet.</p>:notifications.slice(0,8).map(n=><div className="notification" key={n.id}><b>{n.type}</b> — {n.message}</div>)}
      </section>
    </main>
  </div>
}

function Auth({auth,setAuth,submitAuth,error}){
 return <div className="auth"><form onSubmit={submitAuth} className="card authbox">
   <h1>☁️ Cloud Event RSVP</h1><p>Cloud Computing Project</p>{error&&<div className="alert">{error}</div>}
   {auth.mode==="register"&&<input placeholder="Name" value={auth.name} onChange={e=>setAuth({...auth,name:e.target.value})} required/>}
   <input placeholder="Email" type="email" value={auth.email} onChange={e=>setAuth({...auth,email:e.target.value})} required/>
   <input placeholder="Password (8+ chars)" type="password" value={auth.password} onChange={e=>setAuth({...auth,password:e.target.value})} required/>
   {auth.mode==="register"&&<select value={auth.role} onChange={e=>setAuth({...auth,role:e.target.value})}><option>ATTENDEE</option><option>ORGANIZER</option></select>}
   <button>{auth.mode==="login"?"Login":"Create account"}</button>
   <button type="button" className="secondary" onClick={()=>setAuth({...auth,mode:auth.mode==="login"?"register":"login"})}>{auth.mode==="login"?"Need an account? Register":"Already registered? Login"}</button>
 </form></div>
}

function EventPanel({event,counts,selectedRsvp,doRsvp,user,notifications,reload}){
 const [announcement,setAnnouncement]=useState({title:"",message:""});
 const [analytics,setAnalytics]=useState(null);
 useEffect(()=>{api.analytics(event.id).then(setAnalytics).catch(()=>{})},[event.id,counts]);
 const chart=counts?[{name:"Going",value:counts.GOING},{name:"Maybe",value:counts.MAYBE},{name:"Not Going",value:counts.NOT_GOING}]:[];
 async function sendAnnouncement(e){
   e.preventDefault();
   await api.announcement(event.id,announcement); setAnnouncement({title:"",message:""}); await reload();
 }
 return <div>
   <div className="event-head"><div><h2>{event.event_name}</h2><p>{event.description}</p></div><span className="badge">{event.status}</span></div>
   <div className="facts"><span>📅 {event.event_date}</span><span>🕒 {event.start_time}-{event.end_time}</span><span>📍 {event.venue}</span><span>👥 {event.maximum_capacity}</span></div>
   {user.role==="ATTENDEE" && <div className="rsvp-buttons"><button className={selectedRsvp==="GOING"?"selected":""} onClick={()=>doRsvp("GOING")}>GOING</button><button className={selectedRsvp==="MAYBE"?"selected":""} onClick={()=>doRsvp("MAYBE")}>MAYBE</button><button className={selectedRsvp==="NOT_GOING"?"selected":""} onClick={()=>doRsvp("NOT_GOING")}>NOT GOING</button></div>}
   {counts && <div className="stats"><Stat label="Going" value={counts.GOING}/><Stat label="Maybe" value={counts.MAYBE}/><Stat label="Not Going" value={counts.NOT_GOING}/><Stat label="Available" value={counts.available}/></div>}
   {analytics && <div className="charts"><div><h3>RSVP Distribution</h3><ResponsiveContainer width="100%" height={220}><PieChart><Pie data={chart} dataKey="value" nameKey="name" outerRadius={80} label>{chart.map((x,i)=><Cell key={i}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div>
     <div><h3>Capacity</h3><ResponsiveContainer width="100%" height={220}><BarChart data={[{name:"Seats",going:analytics.GOING,available:analytics.available}]}><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="going"/><Bar dataKey="available"/></BarChart></ResponsiveContainer></div></div>}
   {user.role==="ORGANIZER" && <form onSubmit={sendAnnouncement} className="announcement"><h3>Send announcement</h3><input placeholder="Title" value={announcement.title} onChange={e=>setAnnouncement({...announcement,title:e.target.value})} required/><textarea placeholder="Message" value={announcement.message} onChange={e=>setAnnouncement({...announcement,message:e.target.value})} required/><button>Publish</button></form>}
 </div>
}
function Stat({label,value}){return <div className="stat"><b>{value}</b><span>{label}</span></div>}
export default App;
