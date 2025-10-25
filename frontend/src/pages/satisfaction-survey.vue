<script setup lang="ts">
import type { SatisfactionResult } from '../utils/api';

import { ref } from 'vue';
import { analyzeSatisfaction } from '../utils/api';

const analyzing = ref(false);
const result = ref<SatisfactionResult | null>(null);
const error = ref('');

async function captureAndAnalyze() {
  analyzing.value = true;
  error.value = '';
  result.value = null;

  try {
    const response = await analyzeSatisfaction();
    result.value = response;
  } catch (e) {
    error.value = e instanceof Error ? e.message : '分析失败';
  } finally {
    analyzing.value = false;
  }
}

function reset() {
  result.value = null;
  error.value = '';
}

function getScoreColor(score: number): string {
  if (score >= 4)
    return 'text-green-600 dark:text-green-400';
  if (score >= 3)
    return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-600 dark:text-red-400';
}

function getScoreEmoji(score: number): string {
  const emojis = ['😢', '😟', '😐', '😊', '😄'];
  return emojis[score - 1] || '❓';
}

function getSatisfactionLevel(average: number): string {
  if (average >= 4.5)
    return '非常满意';
  if (average >= 3.5)
    return '满意';
  if (average >= 2.5)
    return '一般';
  if (average >= 1.5)
    return '不满意';
  return '非常不满意';
}
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-orange-50 to-amber-100 dark:from-gray-900 dark:to-gray-800">
    <UContainer class="py-8">
      <div class="mb-6">
        <UButton
          to="/"
          variant="ghost"
          icon="i-heroicons-arrow-left"
          size="sm"
        >
          返回首页
        </UButton>
      </div>

      <UCard>
        <template #header>
          <div class="flex items-center gap-3">
            <UIcon name="i-heroicons-face-smile" class="text-2xl text-warning-500" />
            <h1 class="text-2xl font-bold">
              满意度调查
            </h1>
          </div>
          <p class="text-gray-600 dark:text-gray-300 mt-2">
            点击按钮触发后端摄像头拍照，系统将分析游客表情并评估满意度
          </p>
        </template>

        <div class="space-y-6">
          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-camera" class="text-orange-600 dark:text-orange-400 text-xl mt-0.5" />
              <div class="text-sm text-orange-800 dark:text-orange-200">
                <p class="font-medium mb-1">
                  摄像头拍照模式
                </p>
                <p>系统将使用服务器端的摄像头进行拍照，请确保游客在摄像头可视范围内。</p>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <UButton
              color="warning"
              size="lg"
              :disabled="analyzing"
              :loading="analyzing"
              icon="i-heroicons-camera"
              @click="captureAndAnalyze"
            >
              {{ analyzing ? '拍照分析中...' : '拍照并分析' }}
            </UButton>
            <UButton
              color="neutral"
              variant="soft"
              :disabled="analyzing"
              @click="reset"
            >
              清空结果
            </UButton>
          </div>

          <UAlert
            v-if="error"
            color="error"
            variant="soft"
            :title="error"
            icon="i-heroicons-exclamation-triangle"
          />

          <div v-if="result" class="mt-6 space-y-4">
            <UAlert
              v-if="result.count === 0"
              color="info"
              variant="soft"
              title="未识别到人脸"
              description="请上传包含清晰人脸的照片"
              icon="i-heroicons-information-circle"
            />

            <template v-else>
              <UCard color="warning" variant="soft">
                <template #header>
                  <h3 class="font-semibold flex items-center gap-2">
                    <UIcon name="i-heroicons-chart-bar" />
                    总体满意度
                  </h3>
                </template>
                <div class="space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-gray-600 dark:text-gray-300">检测到人数：</span>
                    <span class="font-semibold text-lg">{{ result.count }} 人</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-gray-600 dark:text-gray-300">平均分：</span>
                    <span class="font-semibold text-lg">{{ result.average.toFixed(2) }} 分</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-gray-600 dark:text-gray-300">满意度等级：</span>
                    <span class="font-semibold text-lg">{{ getSatisfactionLevel(result.average) }}</span>
                  </div>
                </div>
              </UCard>

              <UCard>
                <template #header>
                  <h3 class="font-semibold flex items-center gap-2">
                    <UIcon name="i-heroicons-user-group" />
                    个人评分详情
                  </h3>
                </template>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  <div
                    v-for="(score, index) in result.scores"
                    :key="index"
                    class="flex flex-col items-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800"
                  >
                    <span class="text-3xl mb-2">{{ getScoreEmoji(score) }}</span>
                    <span class="text-sm text-gray-600 dark:text-gray-300 mb-1">
                      第 {{ index + 1 }} 人
                    </span>
                    <span
                      class="text-xl font-bold"
                      :class="getScoreColor(score)"
                    >
                      {{ score }} 分
                    </span>
                  </div>
                </div>
              </UCard>

              <UCard color="neutral" variant="soft">
                <template #header>
                  <h3 class="text-sm font-semibold">
                    评分标准
                  </h3>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-5 gap-2 text-sm">
                  <div class="flex items-center gap-2">
                    <span class="text-xl">😄</span>
                    <span>5 分 - 非常开心</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xl">😊</span>
                    <span>4 分 - 开心</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xl">😐</span>
                    <span>3 分 - 平静</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xl">😟</span>
                    <span>2 分 - 不开心</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xl">😢</span>
                    <span>1 分 - 很不开心</span>
                  </div>
                </div>
              </UCard>
            </template>
          </div>
        </div>
      </UCard>

      <UCard class="mt-6" color="neutral" variant="soft">
        <template #header>
          <h3 class="font-semibold">
            使用说明
          </h3>
        </template>
        <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-300">
          <li>点击"拍照并分析"按钮，系统将使用后端摄像头拍摄当前画面</li>
          <li>系统将自动识别所有人脸并分析表情</li>
          <li>每个人脸将获得 1-5 分的满意度评分</li>
          <li>系统会计算平均分和整体满意度等级</li>
          <li>请确保游客在摄像头可视范围内，并保持正面清晰的人脸</li>
        </ul>
      </UCard>
    </UContainer>
  </div>
</template>
