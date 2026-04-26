import { useEffect, useState } from 'react'
import './common/styles/global.css'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

function App() {
  const [backendMessage, setBackendMessage] = useState<string>('Carregando...')

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/hello/`)
      .then((response) => response.json())
      .then((data) => {
        setBackendMessage(data?.message || 'Resposta inválida do backend')
      })
      .catch(() => {
        setBackendMessage('Não foi possível conectar com o backend')
      })
  }, [])

  return (
    <div>
      <h1>🏛️ Sistema Iniciado</h1>
      <p>{backendMessage}</p>
    </div>
  )
}

export default App;
