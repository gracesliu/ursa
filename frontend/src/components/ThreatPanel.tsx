import './ThreatPanel.css'
import type { Threat, Detection } from '../types'

interface ThreatPanelProps {
  threats: Threat[]
  detections: Detection[]
}

export default function ThreatPanel({ threats, detections }: ThreatPanelProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="threat-panel">
      <h2>Threat Detection</h2>
      
      <div className="threat-list">
        {threats.length === 0 && detections.length === 0 ? (
          <div className="empty-state">
            <p>No threats detected</p>
            <span className="empty-subtitle">Start a scenario to see AI detection in action</span>
          </div>
        ) : (
          <>
            {threats.map((threat) => (
              <div key={threat.id} className="threat-item">
                <div className="threat-header">
                  <span className="threat-icon">⚠️</span>
                  <div className="threat-info">
                    <div className="threat-type">{threat.type}</div>
                    <div className="threat-time">{formatTime(threat.timestamp)}</div>
                  </div>
                  <div className="threat-confidence">
                    {(threat.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                {threat.details && (
                  <div className="threat-details">
                    {threat.details.description}
                  </div>
                )}
                <div className="threat-meta">
                  Camera: {threat.camera_id}
                </div>
              </div>
            ))}
            
            {detections.slice(0, 5).map((detection, idx) => (
              <div key={`detection-${idx}`} className="detection-item">
                <div className="detection-header">
                  <span className="detection-icon">🔍</span>
                  <div className="detection-info">
                    <div className="detection-type">{detection.activity_type}</div>
                    <div className="detection-time">{formatTime(detection.timestamp)}</div>
                  </div>
                  <div className="detection-confidence">
                    {(detection.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="detection-meta">
                  Camera: {detection.camera_id}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  )
}

