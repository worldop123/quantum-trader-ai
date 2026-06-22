<template>
  <div class="space-y-6">
    <div class="flex gap-6">
      <!-- Sidebar -->
      <div class="w-48 shrink-0">
        <div class="quantum-card p-2">
          <button v-for="section in sections" :key="section.id"
            @click="activeSection = section.id"
            class="w-full text-left px-3 py-2 rounded text-sm transition-colors"
            :class="activeSection === section.id ? 'bg-quantum-purple/20 text-quantum-purple' : 'text-gray-400 hover:bg-quantum-border/50 hover:text-gray-200'">
            {{ section.name }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 space-y-6">
        <!-- Basic Settings -->
        <div v-if="activeSection === 'basic'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">基本设置</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="quantum-label">系统名称</label>
              <input type="text" class="quantum-input" value="QuantumTrader AI" />
            </div>
            <div>
              <label class="quantum-label">系统版本</label>
              <input type="text" class="quantum-input" value="v1.0.0-beta" disabled />
            </div>
            <div>
              <label class="quantum-label">默认语言</label>
              <select class="quantum-input">
                <option>简体中文</option>
                <option>English</option>
              </select>
            </div>
            <div>
              <label class="quantum-label">时区</label>
              <select class="quantum-input">
                <option>UTC+8 (北京)</option>
                <option>UTC+0 (伦敦)</option>
                <option>UTC-5 (纽约)</option>
              </select>
            </div>
          </div>

          <div class="mt-6 flex justify-end">
            <button class="quantum-btn-primary">保存设置</button>
          </div>
        </div>

        <!-- Trading Settings -->
        <div v-if="activeSection === 'trading'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">交易设置</h3>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">开启现货交易</p>
                <p class="text-xs text-gray-500">允许用户进行现货交易</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">开启合约交易</p>
                <p class="text-xs text-gray-500">允许用户进行合约交易</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">开启期权交易</p>
                <p class="text-xs text-gray-500">允许用户进行期权交易</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">AI 策略交易</p>
                <p class="text-xs text-gray-500">允许用户使用 AI 自动交易策略</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div v-if="activeSection === 'security'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">安全设置</h3>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">登录失败锁定</p>
                <p class="text-xs text-gray-500">连续登录失败 5 次后锁定账户 30 分钟</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">IP 白名单</p>
                <p class="text-xs text-gray-500">仅允许白名单 IP 访问管理后台</p>
              </div>
              <button class="text-quantum-cyan text-sm hover:underline">配置</button>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">操作日志</p>
                <p class="text-xs text-gray-500">记录所有管理员操作</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- About -->
        <div v-if="activeSection === 'about'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">关于系统</h3>
          
          <div class="space-y-4 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">系统名称</span>
              <span class="text-gray-200">QuantumTrader AI 量化交易系统</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">版本号</span>
              <span class="text-gray-200">v1.0.0-beta</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">构建时间</span>
              <span class="text-gray-200">2026-06-20 18:00:00</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">技术栈</span>
              <span class="text-gray-200">Vue 3 + TypeScript + Vite</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">后端框架</span>
              <span class="text-gray-200">Python 3.12 + FastAPI</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">数据库</span>
              <span class="text-gray-200">SQLite + Redis + TimescaleDB</span>
            </div>
            <div class="pt-4 border-t border-quantum-border">
              <p class="text-gray-500 text-xs">© 2026 QuantumTrader AI. All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeSection = ref('basic')

const sections = [
  { id: 'basic', name: '基本设置' },
  { id: 'trading', name: '交易设置' },
  { id: 'security', name: '安全设置' },
  { id: 'about', name: '关于系统' }
]
</script>
