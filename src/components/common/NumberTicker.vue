<template>
  <span class="number-ticker" :class="tickerClass">
    <span class="ticker-value" :class="{ 'flash-up': flashUp, 'flash-down': flashDown }">
      {{ displayValue }}
    </span>
    <span v-if="suffix" class="ticker-suffix">{{ suffix }}</span>
  </span>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'

interface Props {
  value: number
  decimals?: number
  prefix?: string
  suffix?: string
  showSign?: boolean
  flashOnChange?: boolean
  flashDuration?: number
  upColor?: string
  downColor?: string
  neutralColor?: string
  compareValue?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  decimals: 2,
  prefix: '',
  suffix: '',
  showSign: false,
  flashOnChange: true,
  flashDuration: 300,
  upColor: '#00ff88',
  downColor: '#ff4757',
  neutralColor: '#ffffff',
  compareValue: null,
})

const displayValue = ref('')
const flashUp = ref(false)
const flashDown = ref(false)
const prevValue = ref<number | null>(null)

const tickerClass = computed(() => {
  const compare = props.compareValue !== null ? props.compareValue : prevValue.value
  if (compare === null) {
    return 'neutral'
  }
  if (props.value > compare) {
    return 'up'
  } else if (props.value < compare) {
    return 'down'
  }
  return 'neutral'
})

function formatValue(val: number): string {
  let formatted = val.toFixed(props.decimals)
  if (props.showSign && val > 0) {
    formatted = '+' + formatted
  }
  return props.prefix + formatted
}

function animateValue(from: number, to: number, duration: number) {
  const startTime = performance.now()
  const diff = to - from

  function step(currentTime: number) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    // 缓动函数：easeOutCubic
    const easeProgress = 1 - Math.pow(1 - progress, 3)

    const currentValue = from + diff * easeProgress
    displayValue.value = formatValue(currentValue)

    if (progress < 1) {
      requestAnimationFrame(step)
    } else {
      displayValue.value = formatValue(to)
    }
  }

  requestAnimationFrame(step)
}

function triggerFlash(direction: 'up' | 'down') {
  if (!props.flashOnChange) return

  if (direction === 'up') {
    flashUp.value = true
    setTimeout(() => {
      flashUp.value = false
    }, props.flashDuration)
  } else {
    flashDown.value = true
    setTimeout(() => {
      flashDown.value = false
    }, props.flashDuration)
  }
}

watch(() => props.value, (newVal, oldVal) => {
  if (oldVal === undefined || oldVal === null) {
    displayValue.value = formatValue(newVal)
    prevValue.value = newVal
    return
  }

  // 触发闪烁
  if (newVal > oldVal) {
    triggerFlash('up')
  } else if (newVal < oldVal) {
    triggerFlash('down')
  }

  // 平滑动画
  animateValue(oldVal, newVal, 300)

  prevValue.value = newVal
}, { immediate: false })

onMounted(() => {
  displayValue.value = formatValue(props.value)
  prevValue.value = props.value
})
</script>

<style scoped>
.number-ticker {
  display: inline-flex;
  align-items: baseline;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}

.number-ticker.up {
  color: v-bind(upColor);
}

.number-ticker.down {
  color: v-bind(downColor);
}

.number-ticker.neutral {
  color: v-bind(neutralColor);
}

.ticker-value {
  position: relative;
}

.ticker-value.flash-up {
  animation: flashUp 0.3s ease;
}

.ticker-value.flash-down {
  animation: flashDown 0.3s ease;
}

.ticker-suffix {
  margin-left: 2px;
  font-size: 0.85em;
  opacity: 0.8;
}

@keyframes flashUp {
  0% {
    background-color: rgba(0, 255, 136, 0.3);
    text-shadow: 0 0 8px rgba(0, 255, 136, 0.8);
  }
  100% {
    background-color: transparent;
    text-shadow: none;
  }
}

@keyframes flashDown {
  0% {
    background-color: rgba(255, 71, 87, 0.3);
    text-shadow: 0 0 8px rgba(255, 71, 87, 0.8);
  }
  100% {
    background-color: transparent;
    text-shadow: none;
  }
}
</style>
