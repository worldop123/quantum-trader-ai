<template>
  <div class="space-y-6">
    <!-- System Status -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">API 服务</p>
          <Activity class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">延迟: 12ms</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">撮合引擎</p>
          <Zap class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">TPS: 12,450</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">数据库</p>
          <Database class="w-5 h-5 text-quantum-green" />
        </div>
        <p class="text-xl font-bold text-quantum-green">正常</p>
        <p class="text-xs text-gray-500 mt-1">连接数: 234/500</p>
      </div>

      <div class="quantum-card">
        <div class="flex items-center justify-between mb-2">
          <p class="text-gray-500 text-sm">AI 服务</p>
          <Brain class="w-5 h-5 text-quantum-cyan" />
        </div>
        <p class="text-xl font-bold text-quantum-cyan">运行中</p>
        <p class="text-xs text-gray-500 mt-1">GPU 使用率: 67%</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">实时交易量</h3>
        <div class="h-64 flex items-center justify-center bg-quantum-darker rounded-lg">
          <div class="text-center">
            <Activity class="w-12 h-12 text-gray-600 mx-auto mb-2" />
            <p class="text-gray-500 text-sm">实时数据图表开发中</p>
          </div>
        </div>
      </div>

      <div class="quantum-card">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">系统资源使用</h3>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">CPU 使用率</span>
              <span class="text-gray-300 font-mono">45%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-cyan rounded-full" style="width: 45%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">内存使用率</span>
              <span class="text-gray-300 font-mono">62%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-green rounded-full" style="width: 62%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">磁盘使用率</span>
              <span class="text-gray-300 font-mono">38%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-yellow rounded-full" style="width: 38%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-400">网络带宽</span>
              <span class="text-gray-300 font-mono">23%</span>
            </div>
            <div class="h-2 bg-quantum-darker rounded-full overflow-hidden">
              <div class="h-full bg-quantum-purple rounded-full" style="width: 23%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Logs -->
    <div class="quantum-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-200">实时日志</h3>
        <div class="flex gap-2">
          <select class="quantum-input w-28 text-sm">
            <option value="all">全部级别</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <button class="quantum-btn-secondary text-sm">导出日志</button>
        </div>
      </div>
      <div class="bg-quantum-darker rounded-lg p-4 h-64 overflow-auto font-mono text-xs space-y-1">
        <p class="text-gray-500">[2026-06-22 10:30:15] <span class="text-quantum-green">INFO</span> 用户 #10001 登录成功</p>
        <p class="text-gray-500">[2026-06-22 10:30:12] <span class="text-quantum-green">INFO</span> 订单 #1002 撮合成功</p>
        <p class="text-gray-500">[2026-06-22 10:30:08] <span class="text-quantum-yellow">WARN</span> BTC 价格波动超过 3%</p>
        <p class="text-gray-500">[2026-06-22 10:30:05] <span class="text-quantum-green">INFO</span> AI 策略 #1 执行买入操作</p>
        <p class="text-gray-500">[2026-06-22 10:30:01] <span class="text-quantum-green">INFO</span> 系统心跳检测正常</p>
        <p class="text-gray-500">[2026-06-22 10:29:58] <span class="text-quantum-green">INFO</span> 用户 #10005 注册成功</p>
        <p class="text-gray-500">[2026-06-22 10:29:55] <span class="text-quantum-red">ERROR</span> API 请求超时 (重试中...)</p>
        <p class="text-gray-500">[2026-06-22 10:29:52] <span class="text-quantum-green">INFO</span> 数据库备份完成</p>
        <p class="text-gray-500">[2026-06-22 10:29:48] <span class="text-quantum-green">INFO</span> 撮合引擎处理 1,234 笔订单</p>
        <p class="text-gray-500">[2026-06-22 10:29:45] <span class="text-quantum-yellow">WARN</span> 内存使用率接近阈值</p>
        <p class="text-gray-500">[2026-06-22 10:29:40] <span class="text-quantum-green">INFO</span> AI 模型推理完成</p>
        <p class="text-gray-500">[2026-06-22 10:29:35] <span class="text-quantum-green">INFO</span> 缓存刷新完成</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Activity, Zap, Database, Brain } from 'lucide-vue-next'
</script>
