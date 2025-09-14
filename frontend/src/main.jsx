import React from 'react'
import { createRoot } from 'react-dom/client'
import Chat from './widgets/Chat.jsx'

const root = createRoot(document.getElementById('root'))
root.render(
  <React.StrictMode>
    <Chat />
  </React.StrictMode>
)


