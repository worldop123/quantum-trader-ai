<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h3 class="error-title">组件加载失败</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="handleRetry">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          重试
        </button>
      </div>
      <div v-if="showDetails" class="error-details">
        <details>
          <summary>查看错误详情</summary>
          <pre>{{ errorStack }}</pre>
        </details>
      </div>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured, onMounted } from 'vue'

interface Props {
  showDetails?: boolean
  fallback?: string
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true,
  fallback: '',
})

const emit = defineEmits<{
  (e: 'error', error: Error, instance: any, info: string): void
  (e: 'retry'): void
}>()

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message || '未知错误'
  errorStack.value = err.stack || ''

  // 记录错误日志
  console.error('ErrorBoundary caught error:', err)
  console.error('Error info:', info)

  emit('error', err as Error, instance, info)

  // 返回 false 表示继续传播错误
  return false
})

function handleRetry() {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
  emit('retry')
}

// 暴露重置方法
defineExpose({
  reset: handleRetry,
})
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.8) 0%, rgba(15, 20, 30, 0.9) 100%);
  border: 1px solid #2a3441;
  border-radius: 12px;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: #ff4757;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e4e7ed;
}

.error-message {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #8892a6;
  line-height: 1.5;
}

.error-actions {
  margin-bottom: 16px;
}

.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 500;
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

.retry-btn svg {
  width: 14px;
  height: 14px;
}

.error-details {
  text-align: left;
}

.error-details details {
  font-size: 12px;
  color: #8892a6;
}

.error-details summary {
  cursor: pointer;
  padding: 8px 0;
  user-select: none;
}

.error-details summary:hover {
  color: #e4e7ed;
}

.error-details pre {
  margin: 8px 0 0 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 11px;
  line-height: 1.4;
  overflow-x: auto;
  color: #ff6b6b;
}
</style>
