<script setup lang="ts">
const features = [
  {
    title: '景观识别',
    description: '触发后端摄像头拍照，获取相关的中国古代文学作品名句',
    icon: 'i-heroicons-photo',
    color: 'primary' as const,
    to: '/landscape-recognition',
  },
  {
    title: '行程定制',
    description: '根据您的背景和时间，生成个性化的拙政园游览计划',
    icon: 'i-heroicons-map',
    color: 'success' as const,
    to: '/plan-customizing',
  },
  {
    title: '满意度调查',
    description: '触发后端摄像头拍照，分析游客表情并评估满意度',
    icon: 'i-heroicons-face-smile',
    color: 'warning' as const,
    to: '/satisfaction-survey',
  },
];
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <UContainer class="py-12">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          园忆互联
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-300">
          基于 AI 的园林景观识别、行程定制与满意度调查系统
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard
          v-for="feature in features"
          :key="feature.to"
          class="hover:shadow-xl transition-shadow cursor-pointer"
          :ui="{ body: 'p-6' }"
          @click="$router.push(feature.to)"
        >
          <template #header>
            <div class="flex items-center gap-4">
              <UIcon
                :name="feature.icon"
                :class="`text-${feature.color}-500`"
                class="text-3xl"
              />
              <h2 class="text-xl font-semibold">
                {{ feature.title }}
              </h2>
            </div>
          </template>

          <p class="text-gray-600 dark:text-gray-300">
            {{ feature.description }}
          </p>

          <template #footer>
            <UButton
              :color="feature.color"
              variant="soft"
              block
              :to="feature.to"
            >
              开始使用
            </UButton>
          </template>
        </UCard>
      </div>

      <div class="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
        <p>提示：所有功能均需连接到后端 API 服务</p>
      </div>
    </UContainer>
  </div>
</template>
