import { useEffect, useRef, useState } from 'react'

export function useWebSocket(url: string) {
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'Connecting' | 'Open' | 'Closed'>('Connecting')
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    const connect = () => {
      try {
        ws.current = new WebSocket(url)

        ws.current.onopen = () => {
          console.log('WebSocket connected')
          setConnectionStatus('Open')
        }

        ws.current.onmessage = (event) => {
          setLastMessage(event)
        }

        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error)
        }

        ws.current.onclose = () => {
          console.log('WebSocket disconnected')
          setConnectionStatus('Closed')
          
          // Reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 3000)
        }
      } catch (error) {
        console.error('Failed to create WebSocket:', error)
        setConnectionStatus('Closed')
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [url])

  const sendMessage = (message: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message)
    }
  }

  return { lastMessage, sendMessage, connectionStatus }
}

