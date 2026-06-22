<template>
  <nav class="bottom-nav">
    <div class="nav-container">
      <div
        v-for="item in navItems"
        :key="item.path"
        :class="['nav-item', { active: isItemActive(item) }]"
        @click="handleNavClick(item)"
      >
        <div class="nav-icon">
          <component :is="item.icon" />
        </div>
        <span class="nav-label">{{ item.label }}</span>
        <div v-if="item.badge" class="nav-badge">{{ item.badge }}</div>
      </div>
    </div>
    <!-- 安全区域占位 -->
    <div class="safe-area"></div>
  </nav>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface NavItem {
  path: string
  label: string
  icon: any
  badge?: number | string
  matchPrefix?: boolean
}

const route = useRoute()
const router = useRouter()

const currentPath = computed(() => route.path)

// 图标组件（简单的SVG图标）
const HomeIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' }),
  h('polyline', { points: '9 22 9 12 15 12 15 22' }),
])

const TradeIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('polyline', { points: '22 7 13.5 15.5 8.5 10.5 2 17' }),
  h('polyline', { points: '16 7 22 7 22 13' }),
])

const StrategyIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
  h('polyline', { points: '14 2 14 8 20 8' }),
  h('line', { x1: '16', y1: '13', x2: '8', y2: '13' }),
  h('line', { x1: '16', y1: '17', x2: '8', y2: '17' }),
])

const MarketIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('line', { x1: '18', y1: '20', x2: '18', y2: '10' }),
  h('line', { x1: '12', y1: '20', x2: '12', y2: '4' }),
  h('line', { x1: '6', y1: '20', x2: '6', y2: '14' }),
])

const UserIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '12', cy: '7', r: '4' }),
])

const navItems: NavItem[] = [
  {
    path: '/dashboard',
    label: '首页',
    icon: HomeIcon,
  },
  {
    path: '/trade',
    label: '交易',
    icon: TradeIcon,
  },
  {
    path: '/ai-strategy',
    label: '策略',
    icon: StrategyIcon,
  },
  {
    path: '/assets',
    label: '资产',
    icon: MarketIcon,
  },
  {
    path: '/settings',
    label: '设置',
    icon: UserIcon,
  },
]

function isItemActive(item: NavItem): boolean {
  if (item.matchPrefix) {
    return currentPath.value.startsWith(item.path)
  }
  return currentPath.value === item.path
}

function handleNavClick(item: NavItem) {
  if (currentPath.value !== item.path) {
    router.push(item.path)
  }
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(15, 20, 30, 0.95) 0%, rgba(10, 15, 25, 0.98) 100%);
  border-top: 1px solid #2a3441;
  backdrop-filter: blur(20px);
  z-index: 1000;
}

.nav-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 56px;
  padding: 0 8px;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 4px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  color: #8892a6;
  min-height: 44px;
}

.nav-item:active {
  transform: scale(0.95);
}

.nav-item.active {
  color: #00d4ff;
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 22px;
  height: 22px;
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
}

.nav-badge {
  position: absolute;
  top: 2px;
  right: 50%;
  transform: translateX(12px);
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #ff4757;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.safe-area {
  height: env(safe-area-inset-bottom, 0px);
}

/* 仅在移动端显示 */
@media (min-width: 768px) {
  .bottom-nav {
    display: none;
  }
}
</style>
