<script setup lang="ts">
import ErrorBoundary from './components/common/ErrorBoundary.vue'
// QuantumTrader AI - Root Component
</script>

<template>
  <ErrorBoundary>
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </ErrorBoundary>
</template>

<style>
/* Global styles are in style.css */
</style>
