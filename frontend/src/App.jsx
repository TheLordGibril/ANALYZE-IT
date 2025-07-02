import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import AnalyzeIt from './pages/Home'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <AnalyzeIt />
    </>
  )
}

export default App
