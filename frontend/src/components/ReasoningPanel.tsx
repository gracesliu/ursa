import './ReasoningPanel.css'
import type { Reasoning } from '../types'

interface ReasoningPanelProps {
  reasoning: Reasoning[]
}

export default function ReasoningPanel({ reasoning }: ReasoningPanelProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="reasoning-panel">
      <h2>AI Reasoning</h2>
      <p className="panel-subtitle">Real-time agent decision making</p>
      
      <div className="reasoning-list">
        {reasoning.length === 0 ? (
          <div className="empty-state">
            <p>No reasoning logs yet</p>
            <span className="empty-subtitle">AI thinking will appear here during scenarios</span>
          </div>
        ) : (
          reasoning.map((entry, idx) => (
            <div key={idx} className="reasoning-item">
              <div className="reasoning-header">
                <span className="reasoning-icon">🧠</span>
                <div className="reasoning-info">
                  <div className="reasoning-step">{entry.step}</div>
                  <div className="reasoning-time">{formatTime(entry.timestamp)}</div>
                </div>
                <div className="reasoning-camera">{entry.camera_id}</div>
              </div>
              
              <div className="reasoning-content">
                <div className="reasoning-text">{entry.reasoning}</div>
                
                {entry.evidence && entry.evidence.length > 0 && (
                  <div className="reasoning-evidence">
                    <div className="evidence-label">Evidence:</div>
                    <ul>
                      {entry.evidence.map((ev, evIdx) => (
                        <li key={evIdx}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {entry.conclusion && (
                  <div className="reasoning-conclusion">
                    <strong>Conclusion:</strong> {entry.conclusion}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

