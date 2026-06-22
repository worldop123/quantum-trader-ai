<template>
  <div class="ws-status" :class="status" @click="handleClick">
    <span class="status-dot"></span>
    <span class="status-text">{{ statusText }}</span>
    <span v-if="reconnectCount > 0" class="reconnect-count">
      重连中 ({{ reconnectCount }})
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/utils/websocket'

interface Props {
  showText?: boolean
  showReconnectCount?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showText: true,
  showReconnectCount: true,
})

const emit = defineEmits<{
  (e: 'click', status: string): void
}>()

const { status: wsStatus, reconnectCount } = useWebSocket()

const status = computed(() => wsStatus.value)

const statusText = computed(() => {
  switch (wsStatus.value) {
    case 'connected':
      return '已连接'
    case 'connecting':
      return '连接中'
    case 'disconnected':
      return '已断开'
    case 'reconnecting':
      return '重连中'
    default:
      return '未知'
  }
})

function handleClick() {
  emit('click', wsStatus.value)
}
</script>

<style scoped>
.ws-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.ws-status.connected {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
}

.ws-status.connecting {
  background: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.ws-status.disconnected {
  background: rgba(255, 71, 87, 0.1);
  color: #ff4757;
}

.ws-status.reconnecting {
  background: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: relative;
}

.connected .status-dot {
  background: #00ff88;
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.8);
}

.connecting .status-dot {
  background: #ffc107;
  animation: pulse 1.5s ease-in-out infinite;
}

.reconnecting .status-dot {
  background: #ffc107;
  animation: pulse 1s ease-in-out infinite;
}

.disconnected .status-dot {
  background: #ff4757;
  box-shadow: 0 0 8px rgba(255, 71, 87, 0.8);
}

.status-text {
  font-weight: 500;
  line-height: 1;
}

.reconnect-count {
  font-size: 11px;
  opacity: 0.8;
  margin-left: 2px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.ws-status:hover {
  opacity: 0.8;
}

.ws-status:active {
  transform: scale(0.98);
}
</style>
