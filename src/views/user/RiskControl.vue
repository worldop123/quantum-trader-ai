<template>
  <div class="space-y-6">
    <!-- Risk Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">风险等级</p>
          <Shield class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-quantum-green">低风险</p>
        <p class="text-xs text-gray-500 mt-1">当前风险评分: 23/100</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">最大回撤</p>
          <TrendingDown class="w-5 h-5 text-quantum-yellow" />
        </div>
        <p class="text-2xl font-bold text-quantum-yellow font-mono">-5.2%</p>
        <p class="text-xs text-gray-500 mt-1">近30天</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">止损设置</p>
          <Target class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-2xl font-bold text-quantum-cyan font-mono">已启用</p>
        <p class="text-xs text-gray-500 mt-1">全局止损: 10%</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">风控规则</p>
          <CheckCircle class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-2xl font-bold text-gray-200">{{ activeRules }}/{{ totalRules }}</p>
        <p class="text-xs text-gray-500 mt-1">规则已启用</p>
      </div>
    </div>

    <!-- Risk Settings -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Position Risk -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
          <Briefcase class="w-5 h-5 text-quantum-cyan" />
          持仓风控
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">单币种最大持仓比例</p>
              <p class="text-xs text-gray-500">限制单个币种的最大持仓占比</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-quantum-cyan font-mono">30%</span>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">最大持仓数量</p>
              <p class="text-xs text-gray-500">限制同时持有的币种数量</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-quantum-cyan font-mono">10 个</span>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">单仓位最大杠杆</p>
              <p class="text-xs text-gray-500">限制合约交易的最大杠杆倍数</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-quantum-cyan font-mono">20x</span>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stop Loss / Take Profit -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
          <Target class="w-5 h-5 text-quantum-green" />
          止损止盈
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div class="flex items-center gap-3">
              <div>
                <p class="text-sm text-gray-300">全局止损</p>
                <p class="text-xs text-gray-500">总资产亏损达到阈值时自动平仓</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="globalStopLoss" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>

          <div v-if="globalStopLoss" class="p-3 bg-quantum-darker rounded-lg">
            <label class="quantum-label">止损比例</label>
            <div class="flex gap-2">
              <input v-model.number="stopLossPercent" type="number" class="quantum-input flex-1" min="1" max="50" />
              <span class="flex items-center text-gray-400">%</span>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">移动止损</p>
              <p class="text-xs text-gray-500">盈利时自动上移止损位</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="trailingStop" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">自动止盈</p>
              <p class="text-xs text-gray-500">达到目标收益时自动止盈</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="autoTakeProfit" class="sr-only peer" checked>
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- AI Strategy Risk -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
          <Brain class="w-5 h-5 text-quantum-purple" />
          AI策略风控
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">策略最大亏损限制</p>
              <p class="text-xs text-gray-500">单策略最大亏损比例</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-quantum-cyan font-mono">20%</span>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">连续亏损暂停</p>
              <p class="text-xs text-gray-500">连续亏损N次后自动暂停策略</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-quantum-cyan font-mono">5 次</span>
              <button class="text-quantum-cyan text-sm hover:underline">设置</button>
            </div>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">异常波动检测</p>
              <p class="text-xs text-gray-500">检测到异常波动时暂停交易</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Alert Settings -->
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
          <Bell class="w-5 h-5 text-quantum-yellow" />
          风险预警
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">邮件通知</p>
              <p class="text-xs text-gray-500">风险事件发生时发送邮件</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">短信通知</p>
              <p class="text-xs text-gray-500">重要风险事件短信提醒</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>

          <div class="flex items-center justify-between p-3 bg-quantum-darker rounded-lg">
            <div>
              <p class="text-sm text-gray-300">强平预警</p>
              <p class="text-xs text-gray-500">接近强平价时提前预警</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-quantum-green"></div>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end gap-3">
      <button class="quantum-btn-secondary">重置默认</button>
      <button class="quantum-btn-primary" @click="saveSettings">保存设置</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Shield,
  TrendingDown,
  Target,
  CheckCircle,
  Briefcase,
  Brain,
  Bell
} from 'lucide-vue-next'

const globalStopLoss = ref(true)
const stopLossPercent = ref(10)
const trailingStop = ref(false)
const autoTakeProfit = ref(true)

const activeRules = 8
const totalRules = 12

function saveSettings() {
  alert('风控设置已保存')
}
</script>
