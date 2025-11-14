import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import L from 'leaflet'
import type { Camera, Threat, Detection } from '../types'
import CameraFeed from './CameraFeed'
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

// Custom icons
const cameraIcon = L.divIcon({
  className: 'camera-marker',
  html: `<div style="
    width: 24px;
    height: 24px;
    background: #3b82f6;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  "></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
})

const threatIcon = L.divIcon({
  className: 'threat-marker',
  html: `<div style="
    width: 32px;
    height: 32px;
    background: #ef4444;
    border: 3px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(239,68,68,0.5);
    animation: pulse 2s infinite;
  "></div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
})

const detectionIcon = L.divIcon({
  className: 'detection-marker',
  html: `<div style="
    width: 20px;
    height: 20px;
    background: #f59e0b;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(245,158,11,0.4);
  "></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
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
    <MapContainer
      center={center}
      zoom={15}
      style={{ height: '100%', width: '100%' }}
      ref={mapRef}
      zoomControl={true}
    >
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
          <Popup>
            <div style={{ color: '#1f2937' }}>
              <strong>Camera {camera.id}</strong><br />
              {camera.address}<br />
              Status: <span style={{ color: '#10b981' }}>{camera.status}</span>
              {camera.video_url && (
                <>
                  <br />
                  <button
                    onClick={() => setSelectedCamera(camera)}
                    style={{
                      marginTop: '8px',
                      padding: '4px 12px',
                      background: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}
                  >
                    View Feed
                  </button>
                </>
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
          <Popup>
            <div style={{ color: '#1f2937' }}>
              <strong>Detection</strong><br />
              Type: {detection.activity_type}<br />
              Confidence: {(detection.confidence * 100).toFixed(0)}%<br />
              Time: {new Date(detection.timestamp).toLocaleTimeString()}
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Threat markers with alert circles */}
      {threats.map((threat) => (
        <div key={threat.id}>
          <Marker
            position={[threat.location.lat, threat.location.lng]}
            icon={threatIcon}
          >
            <Popup>
              <div style={{ color: '#1f2937' }}>
                <strong>⚠️ Threat Detected</strong><br />
                Type: {threat.type}<br />
                Confidence: {(threat.confidence * 100).toFixed(0)}%<br />
                Camera: {threat.camera_id}<br />
                {threat.details && (
                  <>
                    <br />{threat.details.description}
                  </>
                )}
              </div>
            </Popup>
          </Marker>
          <Circle
            center={[threat.location.lat, threat.location.lng]}
            radius={100}
            pathOptions={{
              color: '#ef4444',
              fillColor: '#ef4444',
              fillOpacity: 0.1,
              weight: 2,
            }}
          />
        </div>
      ))}
      
      {/* Camera Feed Modal */}
      {selectedCamera && (
        <CameraFeed
          camera={selectedCamera}
          onClose={() => setSelectedCamera(null)}
        />
      )}
    </MapContainer>
  )
}

