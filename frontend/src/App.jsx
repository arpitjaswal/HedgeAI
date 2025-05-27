import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import TradingDashboard from './components/TradingDashboard';

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <div className="App">
       <TradingDashboard
        symbols={["BINANCE:BTCUSDT", "BINANCE:SOLUSDT"]}
        timeframes={["1", "5", "15", "60"]}
      />
    </div>
    </>
  )
}

export default App
