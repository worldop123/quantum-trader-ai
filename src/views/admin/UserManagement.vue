<template>
  <div class="space-y-6">
    <!-- Filter Bar -->
    <div class="quantum-card flex flex-wrap items-center gap-4">
      <input v-model="searchQuery" type="text" class="quantum-input w-64" placeholder="搜索用户ID、邮箱、用户名..." />
      <select v-model="filterStatus" class="quantum-input w-32">
        <option value="all">全部状态</option>
        <option value="active">正常</option>
        <option value="disabled">禁用</option>
        <option value="pending">待审核</option>
      </select>
      <select v-model="filterRole" class="quantum-input w-32">
        <option value="all">全部角色</option>
        <option value="user">普通用户</option>
        <option value="vip">VIP用户</option>
        <option value="admin">管理员</option>
      </select>
      <div class="flex-1"></div>
      <button class="quantum-btn-primary text-sm flex items-center gap-2">
        <Plus class="w-4 h-4" />
        添加用户
      </button>
    </div>

    <!-- User Table -->
    <div class="quantum-card overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-quantum-border text-gray-500 text-left">
            <th class="py-3 px-4 font-medium">
              <input type="checkbox" class="rounded border-quantum-border bg-quantum-darker" />
            </th>
            <th class="py-3 px-4 font-medium">用户ID</th>
            <th class="py-3 px-4 font-medium">用户名</th>
            <th class="py-3 px-4 font-medium">邮箱</th>
            <th class="py-3 px-4 font-medium">角色</th>
            <th class="py-3 px-4 font-medium text-right">总资产</th>
            <th class="py-3 px-4 font-medium">状态</th>
            <th class="py-3 px-4 font-medium">注册时间</th>
            <th class="py-3 px-4 font-medium text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" 
            class="border-b border-quantum-border/50 hover:bg-quantum-darker/50 transition-colors">
            <td class="py-3 px-4">
              <input type="checkbox" class="rounded border-quantum-border bg-quantum-darker" />
            </td>
            <td class="py-3 px-4 font-mono text-gray-500 text-xs">#{{ user.id }}</td>
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-quantum-border flex items-center justify-center">
                  <User class="w-4 h-4 text-gray-500" />
                </div>
                <span class="font-medium text-gray-200">{{ user.username }}</span>
              </div>
            </td>
            <td class="py-3 px-4 text-gray-400">{{ user.email }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded"
                :class="{
                  'bg-gray-500/20 text-gray-400': user.role === 'user',
                  'bg-quantum-yellow/20 text-quantum-yellow': user.role === 'vip',
                  'bg-quantum-purple/20 text-quantum-purple': user.role === 'admin'
                }">
                {{ roleLabels[user.role] }}
              </span>
            </td>
            <td class="py-3 px-4 text-right font-mono text-gray-300">${{ user.balance.toLocaleString() }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded"
                :class="{
                  'bg-quantum-green/20 text-quantum-green': user.status === 'active',
                  'bg-quantum-red/20 text-quantum-red': user.status === 'disabled',
                  'bg-quantum-yellow/20 text-quantum-yellow': user.status === 'pending'
                }">
                {{ statusLabels[user.status] }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ user.registerTime }}</td>
            <td class="py-3 px-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <button class="text-quantum-cyan hover:text-cyan-400" title="查看">
                  <Eye class="w-4 h-4" />
                </button>
                <button class="text-quantum-yellow hover:text-yellow-400" title="编辑">
                  <Edit class="w-4 h-4" />
                </button>
                <button class="text-quantum-red hover:text-red-400" title="禁用">
                  <Ban class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <p class="text-sm text-gray-500">共 12,847 条记录，第 1 / 257 页</p>
      <div class="flex gap-2">
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm disabled:opacity-50" disabled>
          上一页
        </button>
        <button class="px-3 py-1 rounded bg-quantum-cyan text-quantum-darker text-sm">1</button>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">2</button>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">3</button>
        <span class="px-3 py-1 text-gray-500 text-sm">...</span>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">257</button>
        <button class="px-3 py-1 rounded bg-quantum-border text-gray-400 hover:bg-gray-700 text-sm">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Plus, Eye, Edit, Ban } from 'lucide-vue-next'

const searchQuery = ref('')
const filterStatus = ref('all')
const filterRole = ref('all')

const roleLabels: Record<string, string> = {
  user: '普通用户',
  vip: 'VIP',
  admin: '管理员'
}

const statusLabels: Record<string, string> = {
  active: '正常',
  disabled: '禁用',
  pending: '待审核'
}

const users = [
  { id: 10001, username: 'test_user', email: 'test@quantumtrader.ai', role: 'user', balance: 100000, status: 'active', registerTime: '2026-01-15' },
  { id: 10002, username: 'trader_pro', email: 'trader@example.com', role: 'vip', balance: 500000, status: 'active', registerTime: '2026-02-20' },
  { id: 10003, username: 'crypto_fan', email: 'crypto@example.com', role: 'user', balance: 25000, status: 'active', registerTime: '2026-03-10' },
  { id: 10004, username: 'quantum_king', email: 'king@example.com', role: 'vip', balance: 1200000, status: 'active', registerTime: '2026-01-05' },
  { id: 10005, username: 'new_user_01', email: 'new01@example.com', role: 'user', balance: 0, status: 'pending', registerTime: '2026-06-22' },
  { id: 10006, username: 'banned_user', email: 'banned@example.com', role: 'user', balance: 5000, status: 'disabled', registerTime: '2026-04-18' },
  { id: 10007, username: 'ai_trader', email: 'ai@example.com', role: 'user', balance: 85000, status: 'active', registerTime: '2026-05-12' },
  { id: 10008, username: 'admin', email: 'admin@quantumtrader.ai', role: 'admin', balance: 9999999, status: 'active', registerTime: '2025-12-01' }
]
</script>
