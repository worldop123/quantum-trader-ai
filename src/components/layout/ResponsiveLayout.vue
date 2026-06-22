<template>
  <div class="responsive-layout" :class="layoutClass">
    <!-- 侧边栏（桌面端） -->
    <aside v-if="showSidebar && isDesktop" class="sidebar">
      <slot name="sidebar"></slot>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header v-if="showHeader" class="header">
        <slot name="header"></slot>
      </header>

      <!-- 内容区 -->
      <div class="content">
        <slot></slot>
      </div>

      <!-- 底部导航栏（移动端） -->
      <nav v-if="showBottomNav && isMobile" class="bottom-nav">
        <slot name="bottom-nav"></slot>
      </nav>
    </main>

    <!-- 移动端侧边栏抽屉 -->
    <div v-if="showSidebar && isMobile && mobileSidebarOpen" class="mobile-sidebar-overlay" @click="closeMobileSidebar">
      <aside class="mobile-sidebar" @click.stop>
        <slot name="sidebar"></slot>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  showSidebar?: boolean
  showHeader?: boolean
  showBottomNav?: boolean
  sidebarWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  showSidebar: true,
  showHeader: true,
  showBottomNav: true,
  sidebarWidth: '240px',
})

const emit = defineEmits<{
  (e: 'mobileSidebarChange', open: boolean): void
}>()

// 响应式断点
const windowWidth = ref(window.innerWidth)
const mobileSidebarOpen = ref(false)

const isMobile = computed(() => windowWidth.value < 768)
const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024)
const isDesktop = computed(() => windowWidth.value >= 1024)

const layoutClass = computed(() => ({
  'is-mobile': isMobile.value,
  'is-tablet': isTablet.value,
  'is-desktop': isDesktop.value,
}))

function handleResize() {
  windowWidth.value = window.innerWidth
}

function openMobileSidebar() {
  mobileSidebarOpen.value = true
  emit('mobileSidebarChange', true)
}

function closeMobileSidebar() {
  mobileSidebarOpen.value = false
  emit('mobileSidebarChange', false)
}

function toggleMobileSidebar() {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
  emit('mobileSidebarChange', mobileSidebarOpen.value)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 暴露方法
defineExpose({
  isMobile,
  isTablet,
  isDesktop,
  openMobileSidebar,
  closeMobileSidebar,
  toggleMobileSidebar,
})
</script>

<style scoped>
.responsive-layout {
  display: flex;
  min-height: 100vh;
  background: #0a0a0f;
}

/* 侧边栏 */
.sidebar {
  width: v-bind(sidebarWidth);
  min-width: v-bind(sidebarWidth);
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* 顶部导航栏 */
.header {
  height: 60px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

/* 内容区 */
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 底部导航栏（移动端） */
.bottom-nav {
  height: 60px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  bottom: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-around;
}

/* 移动端侧边栏遮罩 */
.mobile-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.mobile-sidebar {
  width: 280px;
  height: 100%;
  background: #0a0a0f;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  animation: slideIn 0.3s ease;
  overflow-y: auto;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

/* 平板适配 */
.is-tablet .content {
  padding: 16px;
}

/* 手机适配 */
.is-mobile .content {
  padding: 12px;
}

.is-mobile .header {
  height: 56px;
}

.is-mobile .bottom-nav {
  height: 56px;
}
</style>
