import React from 'react'
import { createRoot } from 'react-dom/client'
import Chat from './widgets/Chat.jsx'
import LineSimulator from './widgets/LineSimulator.jsx'

const root = createRoot(document.getElementById('root'))
function App() {
  const [tab, setTab] = React.useState('chat')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: 12, alignItems: 'center' }}>
        <strong>Chatbot</strong>
        <nav style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setTab('chat')} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #d1d5db', background: tab==='chat' ? '#2563eb' : 'white', color: tab==='chat' ? 'white' : 'black' }}>Chat</button>
          <button onClick={() => setTab('line')} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #d1d5db', background: tab==='line' ? '#2563eb' : 'white', color: tab==='line' ? 'white' : 'black' }}>LINE Simulator</button>
        </nav>
      </header>
      <main style={{ flex: 1 }}>
        {tab === 'chat' ? <Chat /> : <LineSimulator />}
      </main>
    </div>
  )
}

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)


