<script setup lang="ts">
import { ref } from 'vue';
import { analyzeLandscape } from '../utils/api';

const analyzing = ref(false);
const result = ref('');
const error = ref('');

async function captureAndAnalyze() {
  analyzing.value = true;
  error.value = '';
  result.value = '';

  try {
    // 流式接收结果
    await analyzeLandscape((chunk) => {
      result.value += chunk;
    });

    if (!result.value) {
      result.value = '未识别到景观';
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '分析失败';
  } finally {
    analyzing.value = false;
  }
}

function reset() {
  result.value = '';
  error.value = '';
}
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
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
            <UIcon name="i-heroicons-photo" class="text-2xl text-primary-500" />
            <h1 class="text-2xl font-bold">
              景观识别
            </h1>
          </div>
          <p class="text-gray-600 dark:text-gray-300 mt-2">
            点击按钮触发后端摄像头拍照，系统将分析并返回相关的中国古代文学作品名句
          </p>
        </template>

        <div class="space-y-6">
                    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-camera" class="text-blue-600 dark:text-blue-400 text-xl mt-0.5" />
              <div class="text-sm text-blue-800 dark:text-blue-200">
                <p class="font-medium mb-1">
                  摄像头拍照模式
                </p>
                <p>系统将使用服务器端的摄像头进行拍照，请确保拍摄对象在摄像头可视范围内。</p>
              </div>
            </div>
          </div>

                    <div class="flex gap-3">
            <UButton
              color="primary"
              size="lg"
              :disabled="analyzing"
              :loading="analyzing"
              icon="i-heroicons-camera"
              @click="captureAndAnalyze"
            >
              {{ analyzing ? '拍照分析中...' : '拍照并识别' }}
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

                    <div v-if="result" class="mt-6">
            <UCard color="primary" variant="soft">
              <template #header>
                <h3 class="font-semibold flex items-center gap-2">
                  <UIcon name="i-heroicons-sparkles" />
                  识别结果
                </h3>
              </template>
              <div class="prose dark:prose-invert max-w-none">
                <p class="whitespace-pre-wrap text-gray-700 dark:text-gray-200">
                  {{ result }}
                </p>
              </div>
            </UCard>
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
          <li>点击"拍照并识别"按钮，系统将使用后端摄像头拍摄当前画面</li>
          <li>支持的景观类型：山川、河流、湖泊、森林、古建筑、园林、名胜古迹等</li>
          <li>系统将返回与该景观相关的古代文学名句及其出处、作者和背景</li>
          <li>如果图片中没有明显景观，系统将不返回结果</li>
          <li>请确保拍摄对象在摄像头可视范围内</li>
        </ul>
      </UCard>
    </UContainer>
  </div>
</template>
