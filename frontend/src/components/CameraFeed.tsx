import { useState, useEffect, useRef } from 'react'
import type { Camera } from '../types'
import './CameraFeed.css'

interface CameraFeedProps {
  camera: Camera
  onClose: () => void
}

interface Annotation {
  class: string
  confidence: number
  bbox: [number, number, number, number] // [x1, y1, x2, y2]
  center: [number, number]
}

interface AnnotationEntry {
  timestamp: number
  timeString: string
  annotations: Annotation[]
  peopleCount: number
  vehiclesCount: number
  threatDetected: {type: string, confidence: number} | null
}

export default function CameraFeed({ camera, onClose }: CameraFeedProps) {
  const [error, setError] = useState(false)
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [threatDetected, setThreatDetected] = useState<{type: string, confidence: number} | null>(null)
  const [peopleCount, setPeopleCount] = useState(0)
  const [vehiclesCount, setVehiclesCount] = useState(0)
  const [connectionError, setConnectionError] = useState(false)
  const [annotationHistory, setAnnotationHistory] = useState<AnnotationEntry[]>([])
  const [showSidebar, setShowSidebar] = useState(true)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastUpdateTimeRef = useRef<number>(0)
  const annotationThrottleMs = 500 // Update annotations every 500ms instead of every frame

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Connect to video analysis WebSocket with reconnection
  const connectWebSocket = async () => {
    if (!camera.video_url || error) return

    try {
      const configRes = await fetch('http://localhost:8000/api/config')
      const config = await configRes.json()
      
      if (config.use_real_ai) {
        // Close existing connection if any
        if (wsRef.current) {
          wsRef.current.close()
        }

        setIsAnalyzing(true)
        setConnectionError(false)
        const ws = new WebSocket(`ws://localhost:8000/ws/video/${camera.id}`)
        wsRef.current = ws

        ws.onopen = () => {
          setIsAnalyzing(true)
          setConnectionError(false)
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
            reconnectTimeoutRef.current = null
          }
        }

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'video_analysis' && data.annotations) {
            const now = Date.now()
            const video = videoRef.current
            
            // Throttle annotation updates to reduce flashing
            if (now - lastUpdateTimeRef.current >= annotationThrottleMs && video) {
              lastUpdateTimeRef.current = now
              
              const currentTime = video.currentTime
              const timeString = formatTime(currentTime)
              
              const newAnnotations = data.annotations.objects || []
              const newPeopleCount = data.people_count || 0
              const newVehiclesCount = data.vehicles_count || 0
              
              // Update current annotations
              setAnnotations(newAnnotations)
              setPeopleCount(newPeopleCount)
              setVehiclesCount(newVehiclesCount)
              
              // Update threat status
              let threat: {type: string, confidence: number} | null = null
              if (data.threat_detected && data.threat_type) {
                threat = {
                  type: data.threat_type,
                  confidence: data.threat_confidence || 0
                }
                setThreatDetected(threat)
              } else {
                setThreatDetected(null)
              }
              
              // Add to annotation history (only if there are annotations or threat)
              if (newAnnotations.length > 0 || threat) {
                setAnnotationHistory(prev => {
                  const newEntry: AnnotationEntry = {
                    timestamp: currentTime,
                    timeString,
                    annotations: newAnnotations,
                    peopleCount: newPeopleCount,
                    vehiclesCount: newVehiclesCount,
                    threatDetected: threat
                  }
                  
                  // Remove duplicate entries at same timestamp (within 0.5s)
                  const filtered = prev.filter(entry => 
                    Math.abs(entry.timestamp - currentTime) > 0.5
                  )
                  
                  return [...filtered, newEntry].sort((a, b) => a.timestamp - b.timestamp)
                })
              }
            }
          }
        }

        ws.onerror = () => {
          setConnectionError(true)
          setIsAnalyzing(false)
        }

        ws.onclose = () => {
          setIsAnalyzing(false)
          // Attempt to reconnect after 2 seconds
          if (!reconnectTimeoutRef.current) {
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectTimeoutRef.current = null
              connectWebSocket()
            }, 2000)
          }
        }
      } else {
        setIsAnalyzing(false)
      }
    } catch (err) {
      console.error('Failed to connect to video analysis:', err)
      setConnectionError(true)
      setIsAnalyzing(false)
    }
  }

  useEffect(() => {
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [camera.id, camera.video_url, error])

  // Handle video end/restart
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleEnded = () => {
      // Video ended, restart it
      video.currentTime = 0
      video.play().catch(console.error)
    }

    const handlePlay = () => {
      // Video started playing, ensure WebSocket is connected
      if (!isAnalyzing && !wsRef.current) {
        connectWebSocket()
      }
    }

    video.addEventListener('ended', handleEnded)
    video.addEventListener('play', handlePlay)

    return () => {
      video.removeEventListener('ended', handleEnded)
      video.removeEventListener('play', handlePlay)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAnalyzing])

  const handleReset = () => {
    // Reset video
    if (videoRef.current) {
      videoRef.current.currentTime = 0
      videoRef.current.play().catch(console.error)
    }
    
    // Clear annotations
    setAnnotations([])
    setThreatDetected(null)
    setPeopleCount(0)
    setVehiclesCount(0)
    setAnnotationHistory([])
    lastUpdateTimeRef.current = 0
    
    // Reconnect WebSocket
    if (wsRef.current) {
      wsRef.current.close()
    }
    connectWebSocket()
  }

  const handleTimestampClick = (timestamp: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp
      videoRef.current.play().catch(console.error)
    }
  }

  // Draw annotations on canvas
  useEffect(() => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || !annotations.length) return

    const drawAnnotations = () => {
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      // Match canvas size to video
      canvas.width = video.videoWidth || video.clientWidth
      canvas.height = video.videoHeight || video.clientHeight

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw annotations
      annotations.forEach((ann) => {
        const [x1, y1, x2, y2] = ann.bbox
        const scaleX = canvas.width / (video.videoWidth || 1)
        const scaleY = canvas.height / (video.videoHeight || 1)

        const scaledX1 = x1 * scaleX
        const scaledY1 = y1 * scaleY
        const scaledX2 = x2 * scaleX
        const scaledY2 = y2 * scaleY

        // Choose color based on class
        const isPerson = ann.class === 'person'
        const isVehicle = ['car', 'truck', 'bus', 'motorcycle'].includes(ann.class)
        
        ctx.strokeStyle = isPerson ? '#3b82f6' : isVehicle ? '#10b981' : '#f59e0b'
        ctx.lineWidth = 3
        ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1)

        // Draw label background
        const label = `${ann.class} ${(ann.confidence * 100).toFixed(0)}%`
        ctx.font = '16px Arial'
        ctx.fillStyle = ctx.strokeStyle
        const textMetrics = ctx.measureText(label)
        const textWidth = textMetrics.width
        const textHeight = 20

        ctx.fillRect(scaledX1, scaledY1 - textHeight - 5, textWidth + 10, textHeight + 5)

        // Draw label text
        ctx.fillStyle = 'white'
        ctx.fillText(label, scaledX1 + 5, scaledY1 - 8)
      })
    }

    // Draw when video is playing
    const interval = setInterval(drawAnnotations, 100) // Update 10 times per second
    drawAnnotations()

    return () => clearInterval(interval)
  }, [annotations])

  return (
    <div className="camera-feed-overlay" onClick={onClose}>
      <div className="camera-feed-container" onClick={(e) => e.stopPropagation()}>
        <div className="camera-feed-header">
          <div className="camera-feed-info">
            <div className="camera-title-row">
              <h3>Camera {camera.id}</h3>
              {isAnalyzing && (
                <span className="ai-analysis-badge">🤖 AI Analyzing</span>
              )}
              {connectionError && (
                <span className="connection-error-badge">⚠️ Connection Error</span>
              )}
              {threatDetected && (
                <span className="threat-alert-badge">
                  ⚠️ {threatDetected.type} ({(threatDetected.confidence * 100).toFixed(0)}%)
                </span>
              )}
            </div>
            <p>{camera.address}</p>
          </div>
          <div className="camera-feed-actions">
            <button 
              className="camera-feed-toggle-sidebar" 
              onClick={() => setShowSidebar(!showSidebar)}
              title={showSidebar ? "Hide timeline" : "Show timeline"}
            >
              {showSidebar ? '◀' : '▶'} Timeline
            </button>
            <button className="camera-feed-reset" onClick={handleReset} title="Reset video and analysis">
              ↻ Reset
            </button>
            <button className="camera-feed-close" onClick={onClose}>×</button>
          </div>
        </div>
        
        <div className="camera-feed-content">
          <div className="camera-feed-video">
            {camera.video_url && !error ? (
              <div className="video-container">
                <video
                  ref={videoRef}
                  src={camera.video_url}
                  controls
                  autoPlay
                  loop
                  muted
                  onError={() => setError(true)}
                  className="video-player"
                >
                  Your browser does not support the video tag.
                </video>
                <canvas
                  ref={canvasRef}
                  className="annotation-canvas"
                />
              </div>
            ) : (
              <div className="camera-feed-placeholder">
                {error ? (
                  <>
                    <div className="error-icon">⚠️</div>
                    <p>Video not found</p>
                    <p className="error-hint">
                      Please place <code>{camera.video || `${camera.id}.mp4`}</code> in <code>demo/videos/</code>
                    </p>
                  </>
                ) : (
                  <>
                    <div className="loading-icon">📹</div>
                    <p>Loading camera feed...</p>
                  </>
                )}
              </div>
            )}
          </div>
          
          {showSidebar && (
            <div className="annotation-sidebar">
              <div className="annotation-sidebar-header">
                <h4>Detection Timeline</h4>
                <span className="annotation-count">{annotationHistory.length} entries</span>
              </div>
              <div className="annotation-timeline">
                {annotationHistory.length === 0 ? (
                  <div className="timeline-empty">
                    <p>No detections yet</p>
                    <span className="timeline-empty-hint">Annotations will appear here as video plays</span>
                  </div>
                ) : (
                  annotationHistory.map((entry, idx) => (
                    <div 
                      key={idx} 
                      className={`timeline-entry ${entry.threatDetected ? 'timeline-entry-threat' : ''}`}
                      onClick={() => handleTimestampClick(entry.timestamp)}
                    >
                      <div className="timeline-timestamp">{entry.timeString}</div>
                      <div className="timeline-content">
                        {entry.threatDetected && (
                          <div className="timeline-threat">
                            ⚠️ <strong>{entry.threatDetected.type}</strong> ({(entry.threatDetected.confidence * 100).toFixed(0)}%)
                          </div>
                        )}
                        {entry.peopleCount > 0 && (
                          <div className="timeline-detection">
                            👤 {entry.peopleCount} person{entry.peopleCount > 1 ? 's' : ''}
                          </div>
                        )}
                        {entry.vehiclesCount > 0 && (
                          <div className="timeline-detection">
                            🚗 {entry.vehiclesCount} vehicle{entry.vehiclesCount > 1 ? 's' : ''}
                          </div>
                        )}
                        {entry.annotations.length > 0 && (
                          <div className="timeline-objects">
                            {entry.annotations.slice(0, 3).map((ann, annIdx) => (
                              <span key={annIdx} className="timeline-object-tag">
                                {ann.class} ({(ann.confidence * 100).toFixed(0)}%)
                              </span>
                            ))}
                            {entry.annotations.length > 3 && (
                              <span className="timeline-object-tag">+{entry.annotations.length - 3} more</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
        
        <div className="camera-feed-footer">
          <div className="camera-status">
            <span className={`status-indicator ${camera.status === 'active' ? 'active' : 'inactive'}`}></span>
            <span>{camera.status}</span>
          </div>
          <div className="detection-count">
            {peopleCount > 0 && <span>{peopleCount} person(s)</span>}
            {peopleCount > 0 && vehiclesCount > 0 && <span>, </span>}
            {vehiclesCount > 0 && <span>{vehiclesCount} vehicle(s)</span>}
            {peopleCount === 0 && vehiclesCount === 0 && annotations.length === 0 && (
              <span className="no-detections">No objects detected</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

