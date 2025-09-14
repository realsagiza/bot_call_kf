import React, { useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'You are a helpful assistant.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const viewportRef = useRef(null)

  const displayMessages = useMemo(
    () => messages.filter(m => m.role !== 'system'),
    [messages]
  )

  useEffect(() => {
    if (viewportRef.current) {
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight
    }
  }, [displayMessages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const next = [...messages, { role: 'user', content: input }]
    setMessages(next)
    setInput('')
    setLoading(true)
    try {
      const res = await axios.post(`${BACKEND_URL}/api/chat`, {
        messages: next,
      })
      const reply = res.data.reply
      setMessages(curr => [...curr, { role: 'assistant', content: reply }])
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Error'
      setMessages(curr => [...curr, { role: 'assistant', content: `Error: ${msg}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100vh',
      fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial'
    }}>
      <header style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>
        <strong>Chatbot</strong>
      </header>
      <main ref={viewportRef} style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#fafafa' }}>
        {displayMessages.length === 0 && (
          <div style={{ color: '#6b7280' }}>Start chatting...</div>
        )}
        {displayMessages.map((m, idx) => (
          <div key={idx} style={{
            margin: '8px 0',
            display: 'flex',
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{
              maxWidth: 720,
              padding: '8px 12px',
              borderRadius: 12,
              background: m.role === 'user' ? '#2563eb' : '#e5e7eb',
              color: m.role === 'user' ? 'white' : 'black',
              whiteSpace: 'pre-wrap'
            }}>
              {m.content}
            </div>
          </div>
        ))}
      </main>
      <form onSubmit={sendMessage} style={{ display: 'flex', gap: 8, padding: 16, borderTop: '1px solid #e5e7eb' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={loading ? 'Waiting for reply...' : 'Type your message'}
          disabled={loading}
          style={{ flex: 1, fontSize: 16, padding: '10px 12px', borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <button type="submit" disabled={loading} style={{
          background: '#2563eb', color: 'white', padding: '10px 14px', borderRadius: 8, border: 0
        }}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}


