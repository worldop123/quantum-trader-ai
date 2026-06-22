<template>
  <div class="space-y-6">
    <div class="flex gap-6">
      <!-- Sidebar -->
      <div class="w-48 shrink-0">
        <div class="quantum-card p-2">
          <button v-for="section in sections" :key="section.id"
            @click="activeSection = section.id"
            class="w-full text-left px-3 py-2 rounded text-sm transition-colors"
            :class="activeSection === section.id ? 'bg-quantum-cyan/20 text-quantum-cyan' : 'text-gray-400 hover:bg-quantum-border/50 hover:text-gray-200'">
            {{ section.name }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 space-y-6">
        <!-- Profile -->
        <div v-if="activeSection === 'profile'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">个人信息</h3>
          
          <div class="flex items-start gap-6 mb-6">
            <div class="w-20 h-20 rounded-full bg-quantum-border flex items-center justify-center">
              <User class="w-10 h-10 text-gray-500" />
            </div>
            <div>
              <button class="quantum-btn-primary text-sm mb-2">上传头像</button>
              <p class="text-xs text-gray-500">支持 JPG、PNG 格式，大小不超过 2MB</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="quantum-label">用户名</label>
              <input type="text" class="quantum-input" value="test_user" />
            </div>
            <div>
              <label class="quantum-label">邮箱</label>
              <input type="email" class="quantum-input" value="test@quantumtrader.ai" disabled />
            </div>
            <div>
              <label class="quantum-label">手机号</label>
              <input type="tel" class="quantum-input" placeholder="未绑定" />
            </div>
            <div>
              <label class="quantum-label">国家/地区</label>
              <select class="quantum-input">
                <option>中国</option>
                <option>美国</option>
                <option>新加坡</option>
              </select>
            </div>
          </div>

          <div class="mt-6 flex justify-end">
            <button class="quantum-btn-primary">保存修改</button>
          </div>
        </div>

        <!-- Security -->
        <div v-if="activeSection === 'security'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">安全设置</h3>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">登录密码</p>
                <p class="text-xs text-gray-500">定期更换密码可提高账户安全性</p>
              </div>
              <button class="text-quantum-cyan text-sm hover:underline">修改</button>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">资金密码</p>
                <p class="text-xs text-gray-500">用于提现、资金划转等敏感操作</p>
              </div>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">双重验证 (2FA)</p>
                <p class="text-xs text-gray-500">使用 Google Authenticator 增强安全</p>
              </div>
              <span class="text-quantum-yellow text-sm">未启用</span>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">登录设备管理</p>
                <p class="text-xs text-gray-500">查看和管理登录设备</p>
              </div>
              <button class="text-quantum-cyan text-sm hover:underline">管理</button>
            </div>
          </div>
        </div>

        <!-- API -->
        <div v-if="activeSection === 'api'" class="quantum-card">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-200">API 管理</h3>
            <button class="quantum-btn-primary text-sm flex items-center gap-2">
              <Plus class="w-4 h-4" />
              创建 API Key
            </button>
          </div>

          <div class="space-y-3">
            <div class="p-4 bg-quantum-darker rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <p class="font-medium text-gray-200">交易 API</p>
                  <span class="px-2 py-0.5 text-xs rounded bg-quantum-green/20 text-quantum-green">已启用</span>
                </div>
                <div class="flex gap-2">
                  <button class="text-quantum-cyan text-sm hover:underline">编辑</button>
                  <button class="text-quantum-red text-sm hover:underline">删除</button>
                </div>
              </div>
              <p class="text-xs text-gray-500 font-mono">xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</p>
              <p class="text-xs text-gray-600 mt-1">创建于 2026-06-01 · 权限: 读取、交易</p>
            </div>
          </div>
        </div>

        <!-- Preferences -->
        <div v-if="activeSection === 'preferences'" class="quantum-card">
          <h3 class="text-lg font-semibold text-gray-200 mb-6">偏好设置</h3>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">界面语言</p>
                <p class="text-xs text-gray-500">选择显示语言</p>
              </div>
              <select class="quantum-input w-32 text-sm">
                <option>简体中文</option>
                <option>English</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">主题模式</p>
                <p class="text-xs text-gray-500">选择界面主题</p>
              </div>
              <select class="quantum-input w-32 text-sm">
                <option>深色主题</option>
                <option>浅色主题</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">价格小数位</p>
                <p class="text-xs text-gray-500">价格显示的小数位数</p>
              </div>
              <select class="quantum-input w-32 text-sm">
                <option>2 位</option>
                <option>4 位</option>
                <option>6 位</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4 bg-quantum-darker rounded-lg">
              <div>
                <p class="text-gray-200 font-medium">交易确认</p>
                <p class="text-xs text-gray-500">下单前是否需要确认</p>
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
          <h3 class="text-lg font-semibold text-gray-200 mb-6">关于 QuantumTrader AI</h3>
          
          <div class="space-y-4 text-sm text-gray-400">
            <div class="flex justify-between">
              <span>版本</span>
              <span class="text-gray-300">v1.0.0-beta</span>
            </div>
            <div class="flex justify-between">
              <span>构建时间</span>
              <span class="text-gray-300">2026-06-20</span>
            </div>
            <div class="flex justify-between">
              <span>技术支持</span>
              <span class="text-quantum-cyan">support@quantumtrader.ai</span>
            </div>
            <div class="pt-4 border-t border-quantum-border">
              <p class="mb-2">© 2026 QuantumTrader AI. All rights reserved.</p>
              <div class="flex gap-4">
                <a href="#" class="text-quantum-cyan hover:underline">服务条款</a>
                <a href="#" class="text-quantum-cyan hover:underline">隐私政策</a>
                <a href="#" class="text-quantum-cyan hover:underline">风险提示</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Plus } from 'lucide-vue-next'

const activeSection = ref('profile')

const sections = [
  { id: 'profile', name: '个人信息' },
  { id: 'security', name: '安全设置' },
  { id: 'api', name: 'API 管理' },
  { id: 'preferences', name: '偏好设置' },
  { id: 'about', name: '关于我们' }
]
</script>
