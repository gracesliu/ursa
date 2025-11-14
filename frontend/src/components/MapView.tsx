import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import L from 'leaflet'
import type { Camera, Threat, Detection } from '../types'
import CameraFeed from './CameraFeed'
import './MapView.css'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface MapViewProps {
  cameras: Camera[]
  threats: Threat[]
  detections: Detection[]
}

// High-tech camera icon with animated pulse
const cameraIcon = L.divIcon({
  className: 'camera-marker-tech',
  html: `
    <div class="camera-marker-container">
      <div class="camera-marker-pulse"></div>
      <div class="camera-marker-core">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2ZM12 11.5C10.62 11.5 9.5 10.38 9.5 9C9.5 7.62 10.62 6.5 12 6.5C13.38 6.5 14.5 7.62 14.5 9C14.5 10.38 13.38 11.5 12 11.5Z" fill="currentColor"/>
        </svg>
      </div>
      <div class="camera-marker-ring"></div>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
})

// High-tech threat icon with animated alert
const threatIcon = L.divIcon({
  className: 'threat-marker-tech',
  html: `
    <div class="threat-marker-container">
      <div class="threat-marker-pulse"></div>
      <div class="threat-marker-core">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
          <path d="M2 17L12 22L22 17V12L12 17L2 12V17Z" fill="currentColor"/>
        </svg>
      </div>
      <div class="threat-marker-ring"></div>
      <div class="threat-marker-alert"></div>
    </div>
  `,
  iconSize: [40, 40],
  iconAnchor: [20, 20],
})

// High-tech detection icon
const detectionIcon = L.divIcon({
  className: 'detection-marker-tech',
  html: `
    <div class="detection-marker-container">
      <div class="detection-marker-pulse"></div>
      <div class="detection-marker-core">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
          <circle cx="12" cy="12" r="3" fill="currentColor"/>
        </svg>
      </div>
      <div class="detection-marker-ring"></div>
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
})

export default function MapView({ cameras, threats, detections }: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null)
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)

  useEffect(() => {
    if (mapRef.current && cameras.length > 0) {
      const bounds = cameras.map(cam => [cam.lat, cam.lng] as [number, number])
      mapRef.current.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [cameras])

  // Get unique detections by camera (latest per camera)
  const latestDetections = detections.reduce((acc, detection) => {
    if (!acc[detection.camera_id] || 
        new Date(detection.timestamp) > new Date(acc[detection.camera_id].timestamp)) {
      acc[detection.camera_id] = detection
    }
    return acc
  }, {} as Record<string, Detection>)

  const center: [number, number] = cameras.length > 0 
    ? [cameras[0].lat, cameras[0].lng]
    : [37.7749, -122.4194]

  return (
    <div className="map-view-container">
      <MapContainer
        center={center}
        zoom={15}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        zoomControl={true}
        className="tech-map"
      >
        {/* High-tech map tiles with better contrast */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Camera markers */}
        {cameras.map((camera) => (
          <Marker
            key={camera.id}
            position={[camera.lat, camera.lng]}
            icon={cameraIcon}
          >
            <Popup className="tech-popup">
              <div className="popup-content">
                <div className="popup-header">
                  <div className="popup-icon camera-popup-icon">📹</div>
                  <div>
                    <div className="popup-title">Camera {camera.id}</div>
                    <div className="popup-subtitle">{camera.address}</div>
                  </div>
                </div>
                <div className="popup-status">
                  <span className="status-dot-popup"></span>
                  <span className="status-text">{camera.status}</span>
                </div>
                {camera.video_url && (
                  <button
                    className="popup-button"
                    onClick={() => setSelectedCamera(camera)}
                  >
                    <span>View Feed</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M8 5V19L19 12L8 5Z" fill="currentColor"/>
                    </svg>
                  </button>
                )}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Detection markers */}
        {Object.values(latestDetections).map((detection, idx) => (
          <Marker
            key={`detection-${detection.camera_id}-${idx}`}
            position={[detection.location.lat, detection.location.lng]}
            icon={detectionIcon}
          >
            <Popup className="tech-popup">
              <div className="popup-content">
                <div className="popup-header">
                  <div className="popup-icon detection-popup-icon">🔍</div>
                  <div>
                    <div className="popup-title">Detection Alert</div>
                    <div className="popup-subtitle">{detection.activity_type.replace(/_/g, ' ')}</div>
                  </div>
                </div>
                <div className="popup-stats">
                  <div className="stat-item">
                    <span className="stat-label">Confidence</span>
                    <span className="stat-value">{(detection.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Time</span>
                    <span className="stat-value">{new Date(detection.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Threat markers with animated alert circles */}
        {threats.map((threat) => {
          const threatType = threat.type === "lost_pet" ? "🐾" : 
                            threat.type === "wildfire" ? "🔥" : "🦌"
          const threatColor = threat.type === "wildfire" ? "#ef4444" :
                             threat.type === "lost_pet" ? "#f59e0b" : "#ef4444"
          
          return (
            <div key={threat.id}>
              <Marker
                position={[threat.location.lat, threat.location.lng]}
                icon={threatIcon}
              >
                <Popup className="tech-popup threat-popup">
                  <div className="popup-content">
                    <div className="popup-header">
                      <div className="popup-icon threat-popup-icon">{threatType}</div>
                      <div>
                        <div className="popup-title">
                          {threat.type === "lost_pet" ? "Lost Pet Alert" : 
                           threat.type === "wildfire" ? "Wildfire Alert" : 
                           "Detection Alert"}
                        </div>
                        <div className="popup-subtitle">{threat.type.replace(/_/g, ' ')}</div>
                      </div>
                    </div>
                    <div className="popup-stats">
                      <div className="stat-item">
                        <span className="stat-label">Confidence</span>
                        <span className="stat-value threat-stat">{(threat.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Camera</span>
                        <span className="stat-value">{threat.camera_id}</span>
                      </div>
                    </div>
                    {threat.details && (
                      <div className="popup-description">
                        {threat.details.description}
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
              {/* Animated alert circles */}
              <Circle
                center={[threat.location.lat, threat.location.lng]}
                radius={150}
                pathOptions={{
                  color: threatColor,
                  fillColor: threatColor,
                  fillOpacity: 0.15,
                  weight: 3,
                  opacity: 0.6,
                }}
                className="alert-circle-outer"
              />
              <Circle
                center={[threat.location.lat, threat.location.lng]}
                radius={100}
                pathOptions={{
                  color: threatColor,
                  fillColor: threatColor,
                  fillOpacity: 0.25,
                  weight: 2,
                  opacity: 0.8,
                }}
                className="alert-circle-inner"
              />
            </div>
          )
        })}
        
        {/* Camera Feed Modal */}
        {selectedCamera && (
          <CameraFeed
            camera={selectedCamera}
            onClose={() => setSelectedCamera(null)}
          />
        )}
      </MapContainer>
    </div>
  )
}
