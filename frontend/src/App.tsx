import { useState, useEffect } from 'react'
import MapView from './components/MapView'
import ThreatPanel from './components/ThreatPanel'
import ReasoningPanel from './components/ReasoningPanel'
import ControlPanel from './components/ControlPanel'
import { useWebSocket } from './hooks/useWebSocket'
import type { Detection, Threat, Camera, Reasoning } from './types'
import './App.css'

function App() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [threats, setThreats] = useState<Threat[]>([])
  const [detections, setDetections] = useState<Detection[]>([])
  const [reasoning, setReasoning] = useState<Reasoning[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [scenarioRunning, setScenarioRunning] = useState(false)
  const [useRealAI, setUseRealAI] = useState(false)

  const { lastMessage, sendMessage, connectionStatus } = useWebSocket('ws://localhost:8000/ws')

  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data)
      
      switch (data.type) {
        case 'init':
          setCameras(data.cameras || [])
          setThreats(data.threats || [])
          break
        case 'detection':
          if (data.detection) {
            setDetections(prev => [data.detection, ...prev].slice(0, 50))
          }
          if (data.threat) {
            setThreats(prev => [data.threat, ...prev])
          }
          if (data.reasoning) {
            setReasoning(prev => [data.reasoning, ...prev].slice(0, 20))
          }
          break
        case 'scenario_started':
          setScenarioRunning(true)
          break
        case 'scenario_stopped':
          setScenarioRunning(false)
          break
        case 'scenario_summary':
          console.log('Scenario summary:', data)
          break
      }
    }
  }, [lastMessage])

  useEffect(() => {
    setIsConnected(connectionStatus === 'Open')
  }, [connectionStatus])

  useEffect(() => {
    // Fetch initial config
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/config')
        const data = await response.json()
        setUseRealAI(data.use_real_ai || false)
      } catch (error) {
        console.error('Failed to fetch config:', error)
      }
    }
    fetchConfig()
  }, [])

  const startScenario = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scenarios/start?scenario_name=wildlife_detection', {
        method: 'POST',
      })
      const data = await response.json()
      console.log('Scenario started:', data)
    } catch (error) {
      console.error('Failed to start scenario:', error)
    }
  }

  const stopScenario = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scenarios/stop', {
        method: 'POST',
      })
      const data = await response.json()
      console.log('Scenario stopped:', data)
    } catch (error) {
      console.error('Failed to stop scenario:', error)
    }
  }

  const toggleAIMode = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/config/toggle-ai', {
        method: 'POST',
      })
      const data = await response.json()
      setUseRealAI(data.use_real_ai || false)
      console.log('AI mode toggled:', data.mode)
    } catch (error) {
      console.error('Failed to toggle AI mode:', error)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>URSA</h1>
          <p className="subtitle">AI-Powered Wildlife & Wildfire Detection Network</p>
        </div>
        <div className="status-indicator">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <div className="app-content">
        <div className="map-container">
          <MapView
            cameras={cameras}
            threats={threats}
            detections={detections}
          />
        </div>

        <div className="sidebar">
          <ControlPanel
            scenarioRunning={scenarioRunning}
            onStart={startScenario}
            onStop={stopScenario}
            detectionCount={threats.length}
            cameraCount={cameras.length}
            useRealAI={useRealAI}
            onToggleAI={toggleAIMode}
          />
          
          <ThreatPanel threats={threats} detections={detections} />
          
          <ReasoningPanel reasoning={reasoning} />
        </div>
      </div>
    </div>
  )
}

export default App

