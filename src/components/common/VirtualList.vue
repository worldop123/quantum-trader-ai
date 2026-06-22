<template>
  <div ref="containerRef" class="virtual-list" @scroll="handleScroll">
    <div class="virtual-phantom" :style="{ height: totalHeight + 'px' }">
      <div class="virtual-content" :style="{ transform: `translateY(${offsetY}px)` }">
        <slot
          v-for="(item, index) in visibleItems"
          :key="getItemKey(item, startIndex + index)"
          :item="item"
          :index="startIndex + index"
        ></slot>
      </div>
    </div>
    <!-- 空状态 -->
    <div v-if="!loading && items.length === 0" class="empty-state">
      <slot name="empty">
        <span>暂无数据</span>
      </slot>
    </div>
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <slot name="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

interface Props {
  items: any[]
  itemHeight?: number
  estimatedItemHeight?: number
  bufferSize?: number
  loading?: boolean
  getItemKey?: (item: any, index: number) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  itemHeight: 0,
  estimatedItemHeight: 50,
  bufferSize: 5,
  loading: false,
  getItemKey: (item: any, index: number) => index,
})

const emit = defineEmits<{
  (e: 'scroll', event: Event): void
  (e: 'loadMore'): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)
const containerHeight = ref(0)

const itemHeight = computed(() => {
  return props.itemHeight || props.estimatedItemHeight
})

const totalHeight = computed(() => {
  return props.items.length * itemHeight.value
})

const startIndex = computed(() => {
  const start = Math.floor(scrollTop.value / itemHeight.value)
  return Math.max(0, start - props.bufferSize)
})

const endIndex = computed(() => {
  const visibleCount = Math.ceil(containerHeight.value / itemHeight.value)
  const end = startIndex.value + visibleCount + props.bufferSize * 2
  return Math.min(props.items.length, end)
})

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value)
})

const offsetY = computed(() => {
  return startIndex.value * itemHeight.value
})

function handleScroll(event: Event) {
  if (!containerRef.value) return

  scrollTop.value = containerRef.value.scrollTop
  emit('scroll', event)

  // 检查是否滚动到底部，触发加载更多
  const scrollBottom = scrollTop.value + containerHeight.value
  if (scrollBottom >= totalHeight.value - itemHeight.value * 2) {
    emit('loadMore')
  }
}

function updateContainerHeight() {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
  }
}

function scrollToIndex(index: number) {
  if (containerRef.value) {
    containerRef.value.scrollTop = index * itemHeight.value
  }
}

function scrollToTop() {
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
  }
}

function scrollToBottom() {
  if (containerRef.value) {
    containerRef.value.scrollTop = totalHeight.value
  }
}

watch(() => props.items, () => {
  nextTick(() => {
    updateContainerHeight()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    updateContainerHeight()
  })
  window.addEventListener('resize', updateContainerHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerHeight)
})

defineExpose({
  scrollToIndex,
  scrollToTop,
  scrollToBottom,
  updateContainerHeight,
})
</script>

<style scoped>
.virtual-list {
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
  height: 100%;
  -webkit-overflow-scrolling: touch;
}

.virtual-phantom {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: -1;
}

.virtual-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  will-change: transform;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #8892a6;
  font-size: 13px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #2a3441;
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条样式 */
.virtual-list::-webkit-scrollbar {
  width: 6px;
}

.virtual-list::-webkit-scrollbar-track {
  background: #1e2530;
}

.virtual-list::-webkit-scrollbar-thumb {
  background: #3a4451;
  border-radius: 3px;
}

.virtual-list::-webkit-scrollbar-thumb:hover {
  background: #4a5461;
}
</style>
