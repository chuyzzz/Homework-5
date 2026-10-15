import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, ArrowUpRight, CheckCircle2, CircleDollarSign, Play, ShieldCheck, Sparkles } from 'lucide-react'

const API = 'http://localhost:8000'
type Ticket = { id:number; type:string; requester:string; subject:string; status:string; notes?:string; amount?:number }
type AgentEvent = { agent:string; event:string; ticket_id?:number; detail?:string; output?:Record<string, unknown> }
type Result = { agent:string; ticket_id:number; summary:string; facts:Record<string, unknown>; next_action:string; requires_human_approval:boolean }

async function request<T>(path:string, options?:RequestInit):Promise<T> { const r = await fetch(`${API}${path}`, options); if (!r.ok) throw new Error(await r.text()); return r.json() }

export default function App() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [result, setResult] = useState<Result | null>(null)
  const [balance, setBalance] = useState<{balance:number; date:string} | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [approval, setApproval] = useState({ amount:'', kind:'pay', approved_by:'' })

  const load = useCallback(async () => { try { const [t,b,e] = await Promise.all([request<Ticket[]>('/tickets'), request<{balance:number;date:string}>('/cash/checking'), request<AgentEvent[]>('/agent-events?limit=40')]); setTickets(t); setBalance(b); setEvents(e) } catch (e) { setMessage(String(e)) } }, [])
  useEffect(() => { load() }, [load])
  useEffect(() => { const timer = window.setInterval(() => request<AgentEvent[]>('/agent-events?limit=40').then(setEvents).catch(()=>{}), 1500); return () => clearInterval(timer) }, [])
  const current = tickets.find(t => t.id === selected)
  const currentEvents = useMemo(() => events.filter(e => e.ticket_id === selected), [events, selected])
  const run = async () => { if (!selected) return; setBusy(true); setMessage(''); setResult(null); try { const r = await request<Result>(`/tickets/${selected}/run`, { method:'POST' }); setResult(r); await load(); setMessage('Run complete — ticket marked resolved.') } catch(e) { setMessage(String(e)) } finally { setBusy(false) } }
  const approve = async () => { if (!selected) return; try { await request('/approvals', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ ticket_id:selected, amount:Number(approval.amount), kind:approval.kind, approved_by:approval.approved_by }) }); setMessage('Payment approved and balance updated.'); setApproval({amount:'',kind:'pay',approved_by:''}); await load() } catch(e) { setMessage(String(e)) } }

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><div className="brand-mark"><Sparkles size={18}/></div><div><strong>Campus Customs</strong><span>agent operations desk</span></div></div><div className="live"><span className="pulse"/> LIVE CONTROL ROOM</div></header>
    <main>
      <section className="hero"><div><p className="eyebrow">MORNING OPERATIONS · AUG 31</p><h1>Make the next move<br/><em>with evidence.</em></h1><p className="sub">Coordinate the desk, watch every delegation, and keep human approval at the heart of every dollar.</p></div><div className="balance-card"><div className="balance-label"><CircleDollarSign size={18}/> CHECKING BALANCE</div><div className="balance">${balance?.balance.toLocaleString(undefined,{minimumFractionDigits:2}) ?? '—'}</div><small>as of {balance?.date ?? 'loading'}</small></div></section>
      {message && <div className="notice">{message}</div>}
      <div className="grid">
        <section className="tickets card"><div className="section-head"><div><p className="eyebrow">INBOX</p><h2>Desk tickets <span>{tickets.length}</span></h2></div><button className="icon-button" onClick={load}>↻</button></div>
          <div className="ticket-list">{tickets.map(t => <button className={`ticket ${selected===t.id?'selected':''}`} onClick={()=>{setSelected(t.id);setResult(null)}} key={t.id}><div className="ticket-top"><span className={`dot ${t.status==='resolved'?'resolved':''}`}/><b>#{t.id}</b><span className="ticket-type">{t.type.replace('_',' ')}</span><span className="arrow"><ArrowUpRight size={16}/></span></div><strong>{t.subject}</strong><small>{t.requester} · {t.notes}</small><label className={t.status==='resolved'?'done':''}>{t.status}</label></button>)}</div>
        </section>
        <section className="workspace card">{current ? <><div className="workspace-head"><div><p className="eyebrow">TICKET #{current.id} · {current.type.replace('_',' ')}</p><h2>{current.subject}</h2><p className="muted">{current.requester}</p></div><button className="run-button" onClick={run} disabled={busy}><Play size={16} fill="currentColor"/>{busy?'Agents working…':'Run agent team'}</button></div><div className="activity"><div className="activity-title"><Activity size={17}/> LIVE ACTIVITY <span>{currentEvents.length} events</span></div>{currentEvents.length ? currentEvents.map((e,i)=><div className="event" key={i}><span className="event-line"/><div><b>{e.agent}</b><span>{e.event.replace('_',' ')}</span><small>{e.detail || 'Agent completed a step.'}</small></div></div>) : <div className="empty">Run the team to stream delegation and MCP activity here.</div>}</div>{result && <div className="result"><div className="result-title"><CheckCircle2 size={18}/> Agent summary</div><p>{result.summary}</p><div className="agent-chips"><span>{result.agent}</span><span>{result.requires_human_approval?'Human approval required':'Ready'}</span></div></div>}<div className="approve"><div><p className="eyebrow">HUMAN GATE</p><h3>Approve a payment</h3><p className="muted">Agents can prepare. Only you can authorize cash movement.</p></div><div className="approve-form"><input placeholder="Amount" type="number" value={approval.amount} onChange={e=>setApproval({...approval,amount:e.target.value})}/><input placeholder="Your name" value={approval.approved_by} onChange={e=>setApproval({...approval,approved_by:e.target.value})}/><button onClick={approve} disabled={!approval.amount || !approval.approved_by}>Approve pay</button></div></div></> : <div className="empty-select"><ShieldCheck size={40}/><h2>Select a ticket</h2><p>Choose a ticket to inspect its live activity and run the agent team.</p></div>}</section>
      </div>
    </main>
    <footer><span>Campus Customs / MGT 409</span><span>All financial actions require a human click <ShieldCheck size={14}/></span></footer>
  </div>
}
