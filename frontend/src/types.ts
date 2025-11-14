export interface Camera {
  id: string
  lat: number
  lng: number
  address: string
  status: string
  last_activity?: string
  detections?: any[]
  video?: string
  video_url?: string
}

export interface Threat {
  id: string
  type: string
  camera_id: string
  location: {
    lat: number
    lng: number
  }
  confidence: number
  timestamp: string
  status: string
  details?: {
    description: string
    severity: string
    action_required: boolean
  }
}

export interface Detection {
  camera_id: string
  activity_type: string
  confidence: number
  location: {
    lat: number
    lng: number
  }
  timestamp: string
  behavior: string
  details?: {
    description: string
    severity: string
    action_required: boolean
  }
}

export interface Reasoning {
  timestamp: string
  camera_id: string
  step: string
  reasoning: string
  evidence: string[]
  conclusion: string
}

export interface Pattern {
  id: string
  behavior: string
  occurrences: Detection[]
  count: number
  timestamp: number
  predicted_next?: {
    camera_id: string
    location: {
      lat: number
      lng: number
    }
    confidence: number
    reasoning: string
  }
}

