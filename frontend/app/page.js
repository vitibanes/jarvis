'use client'
import { useEffect, useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'

export default function Home() {
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const [tasks, setTasks] = useState([])
  const [logs, setLogs] = useState([])
  const [memory, setMemory] = useState([])
  const [status, setStatus] = useState(null)

  const refresh = async () => {
    const [t, l, m, s] = await Promise.all([
      fetch(`${API}/tasks`).then(r => r.json()),
      fetch(`${API}/logs`).then(r => r.json()),
      fetch(`${API}/memory`).then(r => r.json()),
      fetch(`${API}/status`).then(r => r.json())
    ])
    setTasks(t); setLogs(l); setMemory(m); setStatus(s)
  }

  useEffect(() => { refresh() }, [])

  const send = async () => {
    const r = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ message, task_title: 'Chat from UI' })
    }).then(x => x.json())
    setReply(r.response)
    setMessage('')
    await refresh()
  }

  return (
    <main className="shell">
      <aside className="panel">
        <h2>Tasks</h2>
        {tasks.slice(0,10).map(t => <div key={t.id} className="item">#{t.id} {t.status}<br/>{t.user_input}</div>)}
      </aside>
      <section className="center">
        <h1>JARVIS</h1>
        <p className="subtitle">OpenRouter-first · Request-budgeted · Fallback-aware</p>
        <div className="chatbox">
          <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Ask JARVIS... (try: list)" />
          <button onClick={send}>Send</button>
        </div>
        <div className="reply">{reply}</div>
        {status && <div className="status">
          <b>Health</b> {status.provider_status} | Minute {status.minute_usage}/{status.minute_limit} | Day {status.day_usage}/{status.day_limit}
        </div>}
      </section>
      <aside className="panel">
        <h2>Logs</h2>
        {logs.slice(0,10).map(l => <div key={l.id} className="item">[{l.step_type}] {l.message}</div>)}
        <h2>Memory</h2>
        {memory.slice(0,8).map(m => <div key={m.id} className="item">({m.memory_type}) {m.content}</div>)}
      </aside>
    </main>
  )
}
