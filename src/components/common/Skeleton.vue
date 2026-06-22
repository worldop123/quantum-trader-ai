<template>
  <div class="skeleton-wrapper" :style="{ width, height }">
    <div v-if="variant === 'text'" class="skeleton-text" :style="{ width: textWidth }"></div>
    <div v-else-if="variant === 'circle'" class="skeleton-circle" :style="{ width: size, height: size }"></div>
    <div v-else-if="variant === 'rect'" class="skeleton-rect" :style="{ width, height }"></div>
    <div v-else-if="variant === 'card'" class="skeleton-card">
      <div class="skeleton-card-header">
        <div class="skeleton-circle" style="width: 40px; height: 40px;"></div>
        <div class="skeleton-card-title">
          <div class="skeleton-text" style="width: 120px; margin-bottom: 8px;"></div>
          <div class="skeleton-text" style="width: 80px;"></div>
        </div>
      </div>
      <div class="skeleton-card-body">
        <div class="skeleton-text" style="width: 100%; margin-bottom: 8px;"></div>
        <div class="skeleton-text" style="width: 80%; margin-bottom: 8px;"></div>
        <div class="skeleton-text" style="width: 60%;"></div>
      </div>
    </div>
    <div v-else-if="variant === 'table'" class="skeleton-table">
      <div v-for="i in rows" :key="i" class="skeleton-table-row">
        <div v-for="j in columns" :key="j" class="skeleton-table-cell">
          <div class="skeleton-text" :style="{ width: `${80 + Math.random() * 20}%` }"></div>
        </div>
      </div>
    </div>
    <div v-else-if="variant === 'list'" class="skeleton-list">
      <div v-for="i in rows" :key="i" class="skeleton-list-item">
        <div class="skeleton-circle" style="width: 32px; height: 32px; margin-right: 12px;"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-text" style="width: 60%; margin-bottom: 6px;"></div>
          <div class="skeleton-text" style="width: 40%;"></div>
        </div>
      </div>
    </div>
    <div v-else-if="variant === 'chart'" class="skeleton-chart">
      <div class="skeleton-chart-header">
        <div class="skeleton-text" style="width: 100px;"></div>
      </div>
      <div class="skeleton-chart-body">
        <div class="skeleton-chart-bars">
          <div v-for="i in 12" :key="i" class="skeleton-chart-bar" :style="{ height: `${30 + Math.random() * 70}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'text' | 'circle' | 'rect' | 'card' | 'table' | 'list' | 'chart'
  width?: string
  height?: string
  size?: string
  textWidth?: string
  rows?: number
  columns?: number
  animated?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'text',
  width: '100%',
  height: '16px',
  size: '40px',
  textWidth: '60%',
  rows: 5,
  columns: 4,
  animated: true,
})
</script>

<style scoped>
.skeleton-wrapper {
  display: inline-block;
}

.skeleton-text,
.skeleton-circle,
.skeleton-rect,
.skeleton-table-cell .skeleton-text,
.skeleton-list-content .skeleton-text,
.skeleton-chart-bar {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-text {
  height: 16px;
}

.skeleton-circle {
  border-radius: 50%;
}

.skeleton-rect {
  border-radius: 8px;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.skeleton-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.skeleton-card-title {
  flex: 1;
  margin-left: 12px;
}

.skeleton-card-body .skeleton-text {
  height: 14px;
}

.skeleton-table {
  width: 100%;
}

.skeleton-table-row {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.skeleton-table-cell {
  flex: 1;
  padding: 0 8px;
}

.skeleton-list {
  width: 100%;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.skeleton-list-content {
  flex: 1;
}

.skeleton-list-content .skeleton-text {
  height: 14px;
}

.skeleton-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.skeleton-chart-header {
  margin-bottom: 16px;
}

.skeleton-chart-body {
  height: calc(100% - 40px);
  display: flex;
  align-items: flex-end;
}

.skeleton-chart-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 100%;
  padding: 0 8px;
}

.skeleton-chart-bar {
  width: 8%;
  min-height: 20px;
  border-radius: 4px 4px 0 0;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
