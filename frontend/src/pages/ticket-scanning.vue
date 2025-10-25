<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useQRScanner } from '../utils/useQRScanner';

const videoElement = ref<HTMLVideoElement>();
const { isScanning, scannedCodes, lastScannedCode, scanStatus, statusMessage, startScanning, stopScanning, clearScannedCodes } = useQRScanner({
  correctCode: '114514',
});

const showResults = ref(false);

onMounted(async () => {
  if (videoElement.value) {
    await startScanning(videoElement.value);
  }
});

onUnmounted(() => {
  stopScanning();
});

function handleStopScanning() {
  stopScanning();
}

async function handleStartScanning() {
  if (videoElement.value) {
    await startScanning(videoElement.value);
  }
}

function handleClearResults() {
  clearScannedCodes();
}

function getStatusColor(): 'primary' | 'success' | 'error' | 'warning' {
  switch (scanStatus.value) {
    case 'success':
      return 'success';
    case 'error':
      return 'error';
    case 'scanning':
      return 'primary';
    default:
      return 'warning';
  }
}

function getStatusIcon() {
  switch (scanStatus.value) {
    case 'success':
      return 'i-heroicons-check-circle';
    case 'error':
      return 'i-heroicons-x-circle';
    case 'scanning':
      return 'i-heroicons-camera';
    default:
      return 'i-heroicons-information-circle';
  }
}
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <UContainer class="py-8">
      <!-- 返回按钮 -->
      <div class="mb-6">
        <UButton icon="i-heroicons-arrow-left" variant="ghost" to="/">
          返回首页
        </UButton>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧摄像头区域 -->
        <div class="lg:col-span-2">
          <UCard :ui="{ body: 'p-6' }">
            <template #header>
              <div class="flex items-center justify-between">
                <h2 class="text-2xl font-bold">门票二维码扫描</h2>
                <UIcon :name="getStatusIcon()" :class="`text-${getStatusColor()}-500`" class="text-2xl" />
              </div>
            </template>

            <!-- 摄像头视频显示区 -->
            <div class="mb-6 rounded-lg overflow-hidden bg-black">
              <video
                ref="videoElement"
                autoplay
                playsinline
                class="w-full h-auto aspect-video object-cover"
              />
            </div>

            <!-- 状态信息 -->
            <div class="mb-6">
              <UAlert
                :title="statusMessage || '初始化中...'"
                :icon="getStatusIcon()"
                :color="getStatusColor()"
                class="mb-4"
              />
            </div>

            <!-- 控制按钮 -->
            <div class="flex gap-3">
              <UButton
                v-if="isScanning"
                icon="i-heroicons-stop-circle"
                color="error"
                @click="handleStopScanning"
              >
                停止扫描
              </UButton>
              <UButton
                v-else
                icon="i-heroicons-play-circle"
                color="success"
                @click="handleStartScanning"
              >
                开始扫描
              </UButton>
              <UButton
                icon="i-heroicons-trash"
                color="warning"
                variant="soft"
                @click="handleClearResults"
              >
                清空结果
              </UButton>
              <UButton
                icon="i-heroicons-list-bullet"
                variant="soft"
                @click="showResults = !showResults"
              >
                {{ showResults ? '隐藏' : '显示' }}结果
              </UButton>
            </div>
          </UCard>
        </div>

        <!-- 右侧统计区域 -->
        <div class="lg:col-span-1">
          <!-- 最后扫描 -->
          <UCard v-if="lastScannedCode" class="mb-6" :ui="{ body: 'p-4' }">
            <template #header>
              <h3 class="text-lg font-semibold">最后扫描</h3>
            </template>
            <div class="space-y-2">
              <div class="text-sm text-gray-600 dark:text-gray-400">
                门票号
              </div>
              <div class="text-2xl font-mono font-bold text-primary-500">
                {{ lastScannedCode }}
              </div>
              <div class="pt-2 border-t">
                <div
                class="pt-2 border-t"
                :class="[
                  scanStatus === 'success' && 'text-green-600 dark:text-green-400 font-semibold',
                  scanStatus === 'error' && 'text-red-600 dark:text-red-400 font-semibold',
                ]"
              >
                {{ scanStatus === 'success' ? '✓ 有效门票' : scanStatus === 'error' ? '✗ 无效门票' : '待验证' }}
              </div>
              </div>
            </div>
          </UCard>

          <!-- 统计信息 -->
          <UCard :ui="{ body: 'p-4' }">
            <template #header>
              <h3 class="text-lg font-semibold">扫描统计</h3>
            </template>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-gray-600 dark:text-gray-400">总扫描数</span>
                <span class="text-2xl font-bold text-primary-500">{{ scannedCodes.length }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-600 dark:text-gray-400">扫描状态</span>
                <UBadge
                  :color="getStatusColor()"
                  variant="soft"
                >
                  {{ scanStatus === 'scanning' ? '扫描中...' : scanStatus === 'success' ? '成功' : scanStatus === 'error' ? '失败' : '就绪' }}
                </UBadge>
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- 扫描结果列表 -->
      <UCard v-if="showResults && scannedCodes.length > 0" class="mt-6" :ui="{ body: 'p-6' }">
        <template #header>
          <h3 class="text-lg font-semibold">扫描结果详情</h3>
        </template>

        <div class="space-y-3">
          <div
            v-for="(code, index) in scannedCodes"
            :key="index"
            class="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800"
          >
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                #{{ index + 1 }}
              </div>
              <div class="text-lg font-mono font-bold">
                {{ code }}
              </div>
            </div>
            <div>
              <UBadge
                :color="code === '114514' ? 'success' : 'error'"
                variant="soft"
              >
                {{ code === '114514' ? '✓ 有效' : '✗ 无效' }}
              </UBadge>
            </div>
          </div>
        </div>
      </UCard>

      <!-- 说明信息 -->
      <UCard class="mt-6" color="blue">
        <template #header>
          <h3 class="text-lg font-semibold">使用说明</h3>
        </template>
        <ul class="space-y-2 text-sm">
          <li>• 请确保您的浏览器支持摄像头访问</li>
          <li>• 有效的门票号为：<code class="bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded">114514</code></li>
          <li>• 系统会自动识别扫描的二维码并进行验证</li>
          <li>• 支持连续扫描多个门票</li>
          <li>• 点击"清空结果"可重新开始</li>
        </ul>
      </UCard>
    </UContainer>
  </div>
</template>
