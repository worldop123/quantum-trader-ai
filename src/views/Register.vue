<template>
  <div class="min-h-screen bg-quantum-dark flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-quantum-cyan mb-4 shadow-neon-cyan">
          <Zap class="w-10 h-10 text-quantum-darker" />
        </div>
        <h1 class="text-2xl font-bold neon-text-cyan">QuantumTrader AI</h1>
        <p class="text-gray-500 mt-2">创建您的交易账户</p>
      </div>

      <!-- Register Card -->
      <div class="quantum-card">
        <h2 class="text-xl font-semibold text-gray-200 mb-6 text-center">注册新账户</h2>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="quantum-label">用户名</label>
            <input
              v-model="username"
              type="text"
              class="quantum-input"
              placeholder="请输入用户名"
              required
            />
          </div>

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
              placeholder="请输入密码（至少8位）"
              required
              minlength="8"
            />
          </div>

          <div>
            <label class="quantum-label">确认密码</label>
            <input
              v-model="confirmPassword"
              type="password"
              class="quantum-input"
              placeholder="请再次输入密码"
              required
            />
          </div>

          <div>
            <label class="flex items-start gap-2 cursor-pointer">
              <input type="checkbox" v-model="agreeTerms" class="mt-1 rounded border-quantum-border bg-quantum-darker text-quantum-cyan focus:ring-quantum-cyan" required />
              <span class="text-sm text-gray-400">
                我已阅读并同意
                <a href="#" class="text-quantum-cyan hover:underline">服务条款</a>
                和
                <a href="#" class="text-quantum-cyan hover:underline">隐私政策</a>
              </span>
            </label>
          </div>

          <div v-if="error" class="p-3 rounded bg-quantum-red/10 border border-quantum-red/30 text-quantum-red text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="p-3 rounded bg-quantum-green/10 border border-quantum-green/30 text-quantum-green text-sm">
            注册成功！正在跳转到登录页面...
          </div>

          <button type="submit" class="w-full quantum-btn-primary" :disabled="loading || success">
            <span v-if="loading">注册中...</span>
            <span v-else>注册</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-gray-500 text-sm">
            已有账户？
            <router-link to="/login" class="text-quantum-cyan hover:underline">立即登录</router-link>
          </p>
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

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreeTerms = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref(false)

function handleRegister() {
  error.value = ''
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (password.value.length < 8) {
    error.value = '密码长度至少为8位'
    return
  }

  loading.value = true

  // 模拟网络延迟
  setTimeout(() => {
    const result = userStore.register(email.value, password.value, username.value)
    
    if (result) {
      success.value = true
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      error.value = '注册失败，请重试'
    }
    
    loading.value = false
  }, 1000)
}
</script>
