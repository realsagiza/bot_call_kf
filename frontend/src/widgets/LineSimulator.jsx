import React, { useMemo, useRef, useState, useEffect } from 'react'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export default function LineSimulator() {
  const [userId, setUserId] = useState('UdevUser')
  const [text, setText] = useState('Hello from LINE dev!')
  const [eventsLog, setEventsLog] = useState([])
  const [loading, setLoading] = useState(false)
  const viewportRef = useRef(null)

  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight
    }
  }, [eventsLog])

  const send = async (e) => {
    e.preventDefault()
    if (!text.trim() || loading) return
    setLoading(true)
    try {
      const payload = {
        events: [
          {
            type: 'message',
            replyToken: 'SIMULATED',
            source: { type: 'user', userId },
            message: { type: 'text', text }
          }
        ]
      }
      const res = await axios.post(`${BACKEND_URL}/webhooks/line`, payload)
      setEventsLog(curr => [
        ...curr,
        { dir: 'out', body: payload },
        { dir: 'in', body: res.data }
      ])
      setText('')
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Error'
      setEventsLog(curr => [...curr, { dir: 'error', body: { error: msg } }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <form onSubmit={send} style={{ display: 'flex', gap: 8, padding: 12, borderBottom: '1px solid #e5e7eb' }}>
        <input
          value={userId}
          onChange={e => setUserId(e.target.value)}
          placeholder="userId"
          style={{ width: 220, padding: '8px 10px', borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <input
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder={loading ? 'Sending...' : 'Type a simulated LINE message'}
          disabled={loading}
          style={{ flex: 1, padding: '8px 10px', borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <button type="submit" disabled={loading} style={{ background: '#16a34a', color: 'white', padding: '8px 12px', borderRadius: 8, border: 0 }}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>

      <div ref={viewportRef} style={{ flex: 1, overflowY: 'auto', padding: 12, background: '#fafafa' }}>
        {eventsLog.length === 0 && (
          <div style={{ color: '#6b7280' }}>No events yet. Send a simulated message.</div>
        )}
        {eventsLog.map((e, idx) => (
          <div key={idx} style={{ margin: '8px 0' }}>
            <div style={{ fontSize: 12, color: '#6b7280' }}>{e.dir === 'out' ? 'POST /webhooks/line →' : e.dir === 'in' ? '← response' : 'error'}</div>
            <pre style={{ margin: 0, padding: 12, background: 'white', border: '1px solid #e5e7eb', borderRadius: 8, overflowX: 'auto' }}>
{JSON.stringify(e.body, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  )
}


