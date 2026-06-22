<template>
  <Teleport to="body">
    <!-- 遮罩层 -->
    <Transition name="fade">
      <div v-if="modelValue" class="drawer-mask" @click="handleMaskClick"></div>
    </Transition>

    <!-- 抽屉 -->
    <Transition name="slide">
      <div v-if="modelValue" :class="['drawer', position]" :style="drawerStyle">
        <div class="drawer-header">
          <slot name="header">
            <span class="drawer-title">{{ title }}</span>
          </slot>
          <button v-if="showClose" class="close-btn" @click="handleClose">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div class="drawer-body">
          <slot></slot>
        </div>
        <div v-if="$slots.footer" class="drawer-footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  position?: 'left' | 'right' | 'top' | 'bottom'
  width?: string
  height?: string
  showClose?: boolean
  maskClosable?: boolean
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  position: 'left',
  width: '280px',
  height: '50%',
  showClose: true,
  maskClosable: true,
  zIndex: 1000,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
  (e: 'open'): void
}>()

const drawerStyle = computed(() => {
  const style: Record<string, string> = {
    zIndex: props.zIndex + 1,
  }

  if (props.position === 'left' || props.position === 'right') {
    style.width = props.width
  } else {
    style.height = props.height
  }

  return style
})

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

function handleMaskClick() {
  if (props.maskClosable) {
    handleClose()
  }
}
</script>

<style scoped>
.drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.drawer {
  position: fixed;
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.98) 0%, rgba(15, 20, 30, 0.99) 100%);
  border: 1px solid #2a3441;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
}

.drawer.left {
  top: 0;
  left: 0;
  bottom: 0;
  border-right: 1px solid #2a3441;
  border-radius: 0 12px 12px 0;
}

.drawer.right {
  top: 0;
  right: 0;
  bottom: 0;
  border-left: 1px solid #2a3441;
  border-radius: 12px 0 0 12px;
}

.drawer.top {
  top: 0;
  left: 0;
  right: 0;
  border-bottom: 1px solid #2a3441;
  border-radius: 0 0 12px 12px;
}

.drawer.bottom {
  bottom: 0;
  left: 0;
  right: 0;
  border-top: 1px solid #2a3441;
  border-radius: 12px 12px 0 0;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #2a3441;
  flex-shrink: 0;
}

.drawer-title {
  font-size: 16px;
  font-weight: 600;
  color: #e4e7ed;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #8892a6;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(42, 52, 65, 0.5);
  color: #e4e7ed;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.drawer-footer {
  padding: 16px 20px;
  border-top: 1px solid #2a3441;
  flex-shrink: 0;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 左侧滑入 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.left.slide-enter-from,
.left.slide-leave-to {
  transform: translateX(-100%);
}

.right.slide-enter-from,
.right.slide-leave-to {
  transform: translateX(100%);
}

.top.slide-enter-from,
.top.slide-leave-to {
  transform: translateY(-100%);
}

.bottom.slide-enter-from,
.bottom.slide-leave-to {
  transform: translateY(100%);
}

/* 滚动条样式 */
.drawer-body::-webkit-scrollbar {
  width: 6px;
}

.drawer-body::-webkit-scrollbar-track {
  background: #1e2530;
}

.drawer-body::-webkit-scrollbar-thumb {
  background: #3a4451;
  border-radius: 3px;
}

.drawer-body::-webkit-scrollbar-thumb:hover {
  background: #4a5461;
}
</style>
