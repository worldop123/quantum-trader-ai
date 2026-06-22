<template>
  <div class="space-y-6">
    <!-- Risk Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">系统风险等级</p>
          <Shield class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-quantum-green">低风险</p>
        <p class="text-xs text-gray-500 mt-1">风险评分: 23/100</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">待处理告警</p>
          <AlertTriangle class="w-5 h-5 text-quantum-yellow" />
        </div>
        <p class="text-2xl font-bold text-quantum-yellow">12</p>
        <p class="text-xs text-gray-500 mt-1">需要人工审核</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">今日强平</p>
          <XCircle class="w-5 h-5 text-quantum-red" />
        </div>
        <p class="text-2xl font-bold text-quantum-red">3</p>
        <p class="text-xs text-gray-500 mt-1">涉及金额: $12,450</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">风控规则</p>
          <CheckCircle class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-gray-200">48/50</p>
        <p class="text-xs text-gray-500 mt-1">规则已启用</p>
      </div>
    </div>

    <!-- Risk Settings & Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Global Risk Settings -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">全局风控参数</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">单用户最大持仓比例</p>
              <p class="text-xs text-gray-500">限制单用户总持仓占比</p>
            </div>
            <div class="flex items-center gap-2">
              <input type="number" value="30" class="quantum-input w-20 text-sm text-right" />
              <span class="text-gray-400 text-sm">%</span>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">单币种最大持仓</p>
              <p class="text-xs text-gray-500">限制单币种总持仓量</p>
            </div>
            <div class="flex items-center gap-2">
              <input type="number" value="50" class="quantum-input w-20 text-sm text-right" />
              <span class="text-gray-400 text-sm">%</span>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">最大杠杆倍数</p>
              <p class="text-xs text-gray-500">合约交易最大杠杆</p>
            </div>
            <select class="quantum-input w-24 text-sm">
              <option>10x</option>
              <option>20x</option>
              <option>50x</option>
              <option selected>100x</option>
              <option>125x</option>
            </select>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">异常波动检测</p>
              <p class="text-xs text-gray-500">检测异常价格波动</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Recent Risk Events -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">最近风控事件</h3>
        <div class="space-y-3">
          <div v-for="event in riskEvents" :key="event.id" 
            class="p-3 bg-quantum-darker rounded-lg">
            <div class="flex items-start justify-between mb-1">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 text-xs rounded"
                  :class="{
                    'bg-quantum-red/20 text-quantum-red': event.level === 'high',
                    'bg-quantum-yellow/20 text-quantum-yellow': event.level === 'medium',
                    'bg-quantum-blue/20 text-quantum-blue': event.level === 'low'
                  }">
                  {{ levelLabels[event.level] }}
                </span>
                <span class="text-sm font-medium text-gray-200">{{ event.title }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ event.time }}</span>
            </div>
            <p class="text-xs text-gray-500">{{ event.description }}</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="text-xs text-gray-500">用户: #{{ event.userId }}</span>
              <span class="text-xs text-gray-600">·</span>
              <span class="text-xs text-quantum-cyan cursor-pointer hover:underline">查看详情</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Rules -->
    <div class="quantum-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-200">风控规则管理</h3>
        <button class="quantum-btn-primary text-sm flex items-center gap-2">
          <Plus class="w-4 h-4" />
          添加规则
        </button>
      </div>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-quantum-border text-gray-500 text-left">
            <th class="py-3 px-4 font-medium">规则名称</th>
            <th class="py-3 px-4 font-medium">类型</th>
            <th class="py-3 px-4 font-medium">触发条件</th>
            <th class="py-3 px-4 font-medium">执行动作</th>
            <th class="py-3 px-4 font-medium">状态</th>
            <th class="py-3 px-4 font-medium text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rule in riskRules" :key="rule.id" 
            class="border-b border-quantum-border/50 hover:bg-quantum-darker/50">
            <td class="py-3 px-4 text-gray-200">{{ rule.name }}</td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs rounded bg-quantum-purple/20 text-quantum-purple">
                {{ rule.type }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-400">{{ rule.condition }}</td>
            <td class="py-3 px-4 text-gray-400">{{ rule.action }}</td>
            <td class="py-3 px-4">
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" :checked="rule.enabled" class="sr-only peer">
                <div class="w-9 h-5 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-quantum-green"></div>
              </label>
            </td>
            <td class="py-3 px-4 text-center">
              <button class="text-quantum-cyan hover:text-cyan-400 text-sm mr-2">编辑</button>
              <button class="text-quantum-red hover:text-red-400 text-sm">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Shield, AlertTriangle, XCircle, CheckCircle, Plus } from 'lucide-vue-next'

const levelLabels: Record<string, string> = {
  high: '高危',
  medium: '中危',
  low: '低危'
}

const riskEvents = [
  { id: 1, level: 'high', title: '强制平仓触发', description: '用户 #10008 BTC 合约仓位保证金不足，已强制平仓', time: '10分钟前', userId: 10008 },
  { id: 2, level: 'medium', title: '异常交易检测', description: '检测到用户 #10023 短时间内大量下单，已触发风控审核', time: '25分钟前', userId: 10023 },
  { id: 3, level: 'medium', title: '高波动率警告', description: 'ETH 价格 5 分钟内波动超过 8%', time: '1小时前', userId: 0 },
  { id: 4, level: 'low', title: '大额充值', description: '用户 #10015 充值 50,000 USDT，已自动审核通过', time: '2小时前', userId: 10015 }
]

const riskRules = [
  { id: 1, name: '单日最大亏损限制', type: '账户风控', condition: '单日亏损 > 20%', action: '暂停交易', enabled: true },
  { id: 2, name: '异常下单检测', type: '行为风控', condition: '1分钟内下单 > 50次', action: '限制下单', enabled: true },
  { id: 3, name: '大额提现审核', type: '资金风控', condition: '单笔提现 > 10,000 USDT', action: '人工审核', enabled: true },
  { id: 4, name: '价格波动限制', type: '市场风控', condition: '5分钟波动 > 10%', action: '暂停开仓', enabled: true },
  { id: 5, name: 'IP异常登录', type: '安全风控', condition: '非常用IP登录', action: '短信验证', enabled: false }
]
</script>
