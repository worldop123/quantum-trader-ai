/**
 * WebSocket服务
 * 支持自动重连、心跳保活、订阅机制
 */
import { ref, onUnmounted } from 'vue'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting'

export interface WebSocketMessage {
  type: string
  channel?: string
  data?: any
  timestamp?: number
  [key: string]: any
}

type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string = ''
  private token: string = ''
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private heartbeatInterval: number | null = null
  private heartbeatTimeout = 30000 // 30秒心跳间隔

  // 状态
  public status = ref<WebSocketStatus>('disconnected')
  public connectionCount = ref(0)
  public reconnectCount = ref(0)

  // 消息处理器 {type: [handlers]}
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  // 频道订阅回调 {channel: [callbacks]}
  private channelSubscriptions: Map<string, Set<(data: any) => void>> = new Map()

  constructor() {
    // 使用相对路径，通过vite代理转发到后端
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    this.url = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/ws`
  }

  /**
   * 连接WebSocket
   */
  connect(token?: string): Promise<boolean> {
    if (token) {
      this.token = token
    }

    if (!this.token) {
      console.error('WebSocket: No token provided')
      return Promise.resolve(false)
    }

    return new Promise((resolve) => {
      try {
        this.status.value = 'connecting'

        const wsUrl = `${this.url}?token=${this.token}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected')
          this.status.value = 'connected'
          this.reconnectAttempts = 0
          this.reconnectCount.value = 0
          this.startHeartbeat()
          this.resubscribeAll()
          resolve(true)
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (e) {
            console.error('WebSocket: Failed to parse message', e)
          }
        }

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
        }

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket closed:', event.code, event.reason)
          this.stopHeartbeat()
          this.status.value = 'disconnected'

          // 自动重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect()
          }
        }
      } catch (error) {
        console.error('WebSocket: Connection failed', error)
        this.status.value = 'disconnected'
        resolve(false)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopHeartbeat()
    this.reconnectAttempts = this.maxReconnectAttempts // 阻止自动重连

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.status.value = 'disconnected'
    console.log('🔌 WebSocket manually disconnected')
  }

  /**
   * 重新连接
   */
  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket: Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    this.reconnectCount.value = this.reconnectAttempts
    this.status.value = 'reconnecting'

    // 指数退避算法
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (this.status.value === 'reconnecting') {
        this.connect()
      }
    }, delay)
  }

  /**
   * 发送消息
   */
  send(message: any): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket: Not connected, cannot send message')
      return false
    }

    try {
      this.ws.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('WebSocket: Failed to send message', error)
      return false
    }
  }

  /**
   * 订阅频道
   */
  subscribe(channel: string, callback: (data: any) => void): () => void {
    if (!this.channelSubscriptions.has(channel)) {
      this.channelSubscriptions.set(channel, new Set())
    }

    this.channelSubscriptions.get(channel)!.add(callback)

    // 发送订阅消息
    this.send({
      type: 'subscribe',
      channel: channel
    })

    // 返回取消订阅函数
    return () => {
      this.unsubscribe(channel, callback)
    }
  }

  /**
   * 取消订阅
   */
  unsubscribe(channel: string, callback: (data: any) => void) {
    const callbacks = this.channelSubscriptions.get(channel)
    if (callbacks) {
      callbacks.delete(callback)

      if (callbacks.size === 0) {
        this.channelSubscriptions.delete(channel)
        this.send({
          type: 'unsubscribe',
          channel: channel
        })
      }
    }
  }

  /**
   * 重新订阅所有频道（重连后调用）
   */
  private resubscribeAll() {
    for (const channel of this.channelSubscriptions.keys()) {
      this.send({
        type: 'subscribe',
        channel: channel
      })
    }
    console.log(`🔄 Resubscribed to ${this.channelSubscriptions.size} channels`)
  }

  /**
   * 注册消息类型处理器
   */
  on(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set())
    }

    this.handlers.get(type)!.add(handler)

    return () => {
      this.off(type, handler)
    }
  }

  /**
   * 移除消息处理器
   */
  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  /**
   * 处理收到的消息
   */
  private handleMessage(message: WebSocketMessage) {
    const { type, channel, data } = message

    // 调用类型处理器
    const typeHandlers = this.handlers.get(type)
    if (typeHandlers) {
      typeHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (e) {
          console.error(`WebSocket: Handler error for type ${type}`, e)
        }
      })
    }

    // 调用频道订阅回调
    if (channel) {
      const channelCallbacks = this.channelSubscriptions.get(channel)
      if (channelCallbacks) {
        channelCallbacks.forEach(callback => {
          try {
            callback(data)
          } catch (e) {
            console.error(`WebSocket: Channel callback error for ${channel}`, e)
          }
        })
      }
    }
  }

  /**
   * 启动心跳
   */
  private startHeartbeat() {
    this.stopHeartbeat()

    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, this.heartbeatTimeout)
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 获取连接状态
   */
  getStatus(): WebSocketStatus {
    return this.status.value
  }

  /**
   * 是否连接
   */
  isConnected(): boolean {
    return this.status.value === 'connected'
  }
}

// 创建全局实例
export const wsService = new WebSocketService()

/**
 * Vue组合式函数 - 使用WebSocket
 */
export function useWebSocket() {
  const status = wsService.status
  const reconnectCount = wsService.reconnectCount

  onUnmounted(() => {
    // 组件卸载时不自动断开，因为是全局连接
  })

  return {
    status,
    reconnectCount,
    connect: (token?: string) => wsService.connect(token),
    disconnect: () => wsService.disconnect(),
    subscribe: (channel: string, callback: (data: any) => void) => wsService.subscribe(channel, callback),
    unsubscribe: (channel: string, callback: (data: any) => void) => wsService.unsubscribe(channel, callback),
    send: (message: any) => wsService.send(message),
    on: (type: string, handler: MessageHandler) => wsService.on(type, handler),
    off: (type: string, handler: MessageHandler) => wsService.off(type, handler),
    isConnected: () => wsService.isConnected(),
  }
}

export default wsService
