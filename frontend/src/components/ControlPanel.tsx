import './ControlPanel.css'

interface ControlPanelProps {
  scenarioRunning: boolean
  onStart: () => void
  onStop: () => void
  threatCount: number
  cameraCount: number
  useRealAI: boolean
  onToggleAI: () => void
}

export default function ControlPanel({
  scenarioRunning,
  onStart,
  onStop,
  threatCount,
  cameraCount,
  useRealAI,
  onToggleAI,
}: ControlPanelProps) {
  return (
    <div className="control-panel">
      <h2>Control Center</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{cameraCount}</div>
          <div className="stat-label">Cameras</div>
        </div>
        <div className="stat-card">
          <div className="stat-value threat">{threatCount}</div>
          <div className="stat-label">Active Threats</div>
        </div>
      </div>

      <div className="scenario-controls">
        <h3>AI Mode</h3>
        <div className="ai-mode-toggle">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={useRealAI}
              onChange={onToggleAI}
              className="toggle-input"
            />
            <span className="toggle-slider"></span>
            <span className="toggle-text">
              {useRealAI ? '🤖 Real AI' : '🎭 Simulated'}
            </span>
          </label>
          <p className="toggle-hint">
            {useRealAI 
              ? 'Using computer vision (YOLO + motion detection) to analyze video frames in real-time' 
              : 'Using scripted detections for demo purposes'}
          </p>
        </div>
        
        <h3 style={{ marginTop: '1.5rem' }}>Demo Scenario</h3>
        <p className="scenario-description">
          Car Prowler Detection: {useRealAI ? 'Real AI' : 'Simulated'} mode detecting suspicious activity across multiple cameras
        </p>
        
        {!scenarioRunning ? (
          <button className="btn btn-primary" onClick={onStart}>
            Start Scenario
          </button>
        ) : (
          <button className="btn btn-danger" onClick={onStop}>
            Stop Scenario
          </button>
        )}
      </div>
    </div>
  )
}

