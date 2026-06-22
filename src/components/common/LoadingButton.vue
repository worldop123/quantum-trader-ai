<template>
  <button
    :class="[
      'loading-button',
      type,
      size,
      {
        loading: loading,
        disabled: disabled || loading,
        block: block,
      },
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-spinner">
      <svg class="spinner" viewBox="0 0 24 24" fill="none">
        <circle class="spinner-track" cx="12" cy="12" r="10" stroke-width="2" />
        <path class="spinner-path" d="M12 2a10 10 0 0 1 10 10" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>
    <span v-else class="btn-icon" v-if="icon">
      <component :is="icon" />
    </span>
    <span class="btn-text">
      <slot>{{ loading ? loadingText : text }}</slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'default'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  disabled?: boolean
  block?: boolean
  text?: string
  loadingText?: string
  icon?: any
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  loading: false,
  disabled: false,
  block: false,
  text: '提交',
  loadingText: '加载中...',
  icon: null,
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

function handleClick(event: MouseEvent) {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.loading-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  user-select: none;
  position: relative;
  overflow: hidden;
}

.loading-button.block {
  width: 100%;
}

.loading-button.small {
  padding: 4px 12px;
  font-size: 12px;
  border-radius: 6px;
}

.loading-button.large {
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 10px;
}

/* Primary */
.loading-button.primary {
  background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
  color: #fff;
  border-color: #00d4ff;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

.loading-button.primary:hover:not(:disabled):not(.loading) {
  background: linear-gradient(135deg, #33ddff 0%, #00aadd 100%);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
  transform: translateY(-1px);
}

.loading-button.primary:active:not(:disabled):not(.loading) {
  transform: translateY(0);
}

/* Success */
.loading-button.success {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #fff;
  border-color: #00ff88;
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
}

.loading-button.success:hover:not(:disabled):not(.loading) {
  background: linear-gradient(135deg, #33ff9f 0%, #00dd77 100%);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
  transform: translateY(-1px);
}

/* Warning */
.loading-button.warning {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
  color: #fff;
  border-color: #ffc107;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.loading-button.warning:hover:not(:disabled):not(.loading) {
  background: linear-gradient(135deg, #ffcd38 0%, #ffa726 100%);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.4);
  transform: translateY(-1px);
}

/* Danger */
.loading-button.danger {
  background: linear-gradient(135deg, #ff4757 0%, #ff2d3f 100%);
  color: #fff;
  border-color: #ff4757;
  box-shadow: 0 2px 8px rgba(255, 71, 87, 0.3);
}

.loading-button.danger:hover:not(:disabled):not(.loading) {
  background: linear-gradient(135deg, #ff6b7a 0%, #ff4757 100%);
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.4);
  transform: translateY(-1px);
}

/* Default */
.loading-button.default {
  background: rgba(42, 52, 65, 0.8);
  color: #e4e7ed;
  border-color: #2a3441;
}

.loading-button.default:hover:not(:disabled):not(.loading) {
  background: rgba(52, 62, 75, 0.9);
  border-color: #3a4451;
}

/* Disabled & Loading */
.loading-button:disabled,
.loading-button.loading {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.loading-button.loading {
  pointer-events: none;
}

/* Spinner */
.btn-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
}

.spinner {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

.small .spinner {
  width: 12px;
  height: 12px;
}

.large .spinner {
  width: 20px;
  height: 20px;
}

.spinner-track {
  stroke: rgba(255, 255, 255, 0.2);
}

.spinner-path {
  stroke: #fff;
  animation: dash 1.5s ease-in-out infinite;
}

.default .spinner-track {
  stroke: rgba(255, 255, 255, 0.1);
}

.default .spinner-path {
  stroke: #00d4ff;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon svg {
  width: 16px;
  height: 16px;
}

.small .btn-icon svg {
  width: 12px;
  height: 12px;
}

.large .btn-icon svg {
  width: 20px;
  height: 20px;
}

.btn-text {
  line-height: 1;
}
</style>
