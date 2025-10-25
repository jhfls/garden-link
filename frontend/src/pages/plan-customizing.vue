<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui';
import { ref } from 'vue';
import { customizePlan } from '@/utils/api';
import { useSpeech } from '@/utils/useSpeech';

const state = ref({
  priorKnowledge: '',
  duration: '',
  preferences: [] as string[],
  otherPreference: '',
});

const preferenceOptions = ['建筑美学', '园林艺术', '历史文化', '植物景观', '摄影打卡', '安静休闲'];
const hasOtherPreference = ref(false);
const generating = ref(false);
const result = ref('');

// 初始化朗读功能
const { isSpeaking, isSpeechEnabled, queueSpeech, toggleSpeech, stopSpeech, setGenerating } = useSpeech({
  lang: 'zh-CN',
  rate: 0.9,
});

async function onSubmit(event: FormSubmitEvent<typeof state.value>) {
  generating.value = true;
  result.value = '';
  stopSpeech();
  setGenerating(true);

  try {
    const allPreferences = [...event.data.preferences];
    if (event.data.otherPreference?.trim())
      allPreferences.push(event.data.otherPreference.trim());
    await customizePlan(
      event.data.priorKnowledge?.trim() || '没有特别了解',
      event.data.duration.trim(),
      allPreferences,
      (chunk) => {
        result.value += chunk;
        queueSpeech(chunk);
      },
    );
  } catch (e) {
    const toast = useToast();
    toast.add({
      title: '生成失败',
      description: e instanceof Error ? e.message : '未知错误',
      color: 'error',
    });
  } finally {
    generating.value = false;
    setGenerating(false);
  }
}
</script>

<template>
  <div class="min-h-screen bg-linear-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800">
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
            <UIcon name="i-heroicons-map" class="text-2xl text-success-500" />
            <h1 class="text-2xl font-bold">
              行程定制
            </h1>
          </div>
          <p class="text-gray-600 dark:text-gray-300 mt-2">
            根据您的背景和时间，为您生成个性化的拙政园游览计划
          </p>
        </template>

        <UForm :state class="space-y-6" @submit="onSubmit">
          <UFormField label="您对拙政园的了解" name="priorKnowledge">
            <UTextarea
              v-model="state.priorKnowledge"
              class="w-full"
              placeholder="可以随便说说您知道的内容，如：拙政园是江南四大名园之一..."
              :rows="4"
            />
          </UFormField>

          <UFormField label="预计游览时间" name="duration" required>
            <UInput
              v-model="state.duration"
              placeholder="2 小时"
            />
          </UFormField>

          <UFormField label="游览偏好" name="preferences">
            <UCheckboxGroup
              v-model="state.preferences"
              :items="preferenceOptions"
              orientation="horizontal"
            />
            <div class="flex flex-col gap-2">
              <UCheckbox v-model="hasOtherPreference" label="其他" />
              <UInput
                v-if="hasOtherPreference"
                v-model="state.otherPreference"
                placeholder="请输入其他偏好"
                size="sm"
                class="w-80"
                required
              />
            </div>
          </UFormField>

          <UButton type="submit" color="success" :loading="generating">
            生成游览计划
          </UButton>

          <div v-if="result" class="mt-6 relative flex w-full flex-col rounded-lg border border-muted">
            <UCard color="success" variant="soft">
              <template #header>
                <div class="flex items-center justify-between w-full">
                  <h3 class="font-semibold flex items-center gap-2">
                    <UIcon name="i-heroicons-sparkles" />
                    您的专属游览计划
                  </h3>
                  <div class="flex items-center gap-2">
                    <UButton
                      v-if="isSpeechEnabled"
                      :icon="isSpeaking ? 'i-heroicons-pause-solid' : 'i-heroicons-speaker-wave-solid'"
                      :color="isSpeaking ? 'warning' : 'success'"
                      variant="ghost"
                      size="sm"
                      :title="isSpeaking ? '暂停朗读' : '开始朗读'"
                      @click="toggleSpeech"
                    />
                    <UButton
                      v-if="isSpeaking"
                      icon="i-heroicons-stop-solid"
                      color="error"
                      variant="ghost"
                      size="sm"
                      title="停止朗读"
                      @click="stopSpeech"
                    />
                    <UToggle
                      v-model="isSpeechEnabled"
                      :title="isSpeechEnabled ? '禁用朗读' : '启用朗读'"
                      @change="() => isSpeechEnabled ? undefined : stopSpeech()"
                    />
                  </div>
                </div>
              </template>
              <div class="prose dark:prose-invert max-w-none">
                <div class="whitespace-pre-wrap text-gray-700 dark:text-gray-200">
                  {{ result }}
                </div>
              </div>
            </UCard>
            <BorderBeam
              :size="250"
              :duration="12"
              :delay="9"
              :border-width="2"
            />
          </div>
        </UForm>
      </UCard>

      <UCard class="mt-6" color="neutral" variant="soft">
        <template #header>
          <h3 class="font-semibold">
            关于拙政园
          </h3>
        </template>
        <div class="text-sm text-gray-600 dark:text-gray-300 space-y-2">
          <p>
            拙政园是江南古典园林的代表作之一，始建于明代正德年间，由王献臣建造。
            园林占地约 5.2 公顷，分为东、中、西三部分。
          </p>
          <p>
            主要景点包括：远香堂、香洲、见山楼、梧竹幽居、玉兰堂等。
            园林设计体现了文人园林的精髓，蕴含着丰富的文化内涵。
          </p>
        </div>
      </UCard>
    </UContainer>
  </div>
</template>
