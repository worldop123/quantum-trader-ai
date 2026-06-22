<template>
  <div class="min-h-screen bg-quantum-dark flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-quantum-cyan mb-4 shadow-neon-cyan">
          <Zap class="w-10 h-10 text-quantum-darker" />
        </div>
        <h1 class="text-2xl font-bold neon-text-cyan">QuantumTrader AI</h1>
        <p class="text-gray-500 mt-2">下一代AI量化交易系统</p>
      </div>

      <!-- Login Card -->
      <div class="quantum-card">
        <h2 class="text-xl font-semibold text-gray-200 mb-6 text-center">登录账户</h2>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="quantum-label">邮箱地址</label>
            <input
              v-model="email"
              type="email"
              class="quantum-input"
              placeholder="请输入邮箱"
              required
            />
          </div>

          <div>
            <label class="quantum-label">密码</label>
            <input
              v-model="password"
              type="password"
              class="quantum-input"
              placeholder="请输入密码"
              required
            />
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="rememberMe" class="rounded border-quantum-border bg-quantum-darker text-quantum-cyan focus:ring-quantum-cyan" />
              <span class="text-sm text-gray-400">记住我</span>
            </label>
            <a href="#" class="text-sm text-quantum-cyan hover:underline">忘记密码？</a>
          </div>

          <div v-if="error" class="p-3 rounded bg-quantum-red/10 border border-quantum-red/30 text-quantum-red text-sm">
            {{ error }}
          </div>

          <button type="submit" class="w-full quantum-btn-primary" :disabled="loading">
            <span v-if="loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-gray-500 text-sm">
            还没有账户？
            <router-link to="/register" class="text-quantum-cyan hover:underline">立即注册</router-link>
          </p>
        </div>

        <!-- Demo Accounts -->
        <div class="mt-6 pt-6 border-t border-quantum-border">
          <p class="text-xs text-gray-500 text-center mb-3">测试账号</p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <button @click="fillUserAccount" class="p-2 rounded border border-quantum-border hover:bg-quantum-border/30 transition-colors text-left">
              <p class="text-gray-400">普通用户</p>
              <p class="text-quantum-cyan font-mono">test@quantumtrader.ai</p>
            </button>
            <button @click="fillAdminAccount" class="p-2 rounded border border-quantum-border hover:bg-quantum-border/30 transition-colors text-left">
              <p class="text-gray-400">管理员</p>
              <p class="text-quantum-purple font-mono">admin@quantumtrader.ai</p>
            </button>
          </div>
        </div>
      </div>

      <p class="text-center text-gray-600 text-xs mt-8">
        © 2026 QuantumTrader AI. All rights reserved.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Zap } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

function handleLogin() {
  loading.value = true
  error.value = ''

  // 模拟网络延迟
  setTimeout(() => {
    const success = userStore.login(email.value, password.value)
    
    if (success) {
      if (userStore.isAdmin) {
        router.push('/admin/dashboard')
      } else {
        router.push('/dashboard')
      }
    } else {
      error.value = '邮箱或密码错误，请重试'
    }
    
    loading.value = false
  }, 800)
}

function fillUserAccount() {
  email.value = 'test@quantumtrader.ai'
  password.value = 'Test123456'
}

function fillAdminAccount() {
  email.value = 'admin@quantumtrader.ai'
  password.value = 'Admin123456'
}
</script>
