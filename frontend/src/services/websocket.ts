import { useAuthStore } from '../store/authStore'

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  connect() {
    const token = useAuthStore.getState().token
    if (!token) {
      console.error('WebSocket bağlantısı için token gerekli')
      return
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    this.ws = new WebSocket(`${wsUrl}/api/ws?token=${token}`)

    this.ws.onopen = () => {
      console.log('WebSocket bağlantısı kuruldu')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.notifyListeners(data.type || 'message', data)
      } catch (error) {
        console.error('WebSocket mesaj parse hatası:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket hatası:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket bağlantısı kapandı')
      this.attemptReconnect()
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`WebSocket yeniden bağlanma denemesi ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
        this.connect()
      }, this.reconnectDelay)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: (data: any) => void) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.delete(callback)
    }
  }

  private notifyListeners(event: string, data: any) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach((callback) => callback(data))
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

export const wsService = new WebSocketService()

