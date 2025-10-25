<script setup lang="ts">
import { ref, watch } from 'vue';

const show = defineModel<boolean>('show');
const saving = ref(false);
const backendUrl = ref('');

watch(show, (x) => {
  if (x)
    backendUrl.value = localStorage.getItem('backend-url') || '';
});

function onSave() {
  saving.value = true;
  localStorage.setItem('backend-url', backendUrl.value);
  location.reload();
}
</script>

<template>
  <UModal v-model:open="show" title="设置" :ui="{ footer: 'grid grid-cols-2' }">
    <template #body>
      <UFormField class="flex items-center gap-4" label="后端 URL" name="backendUrl">
        <UInput v-model="backendUrl" placeholder="http://localhost:8908" />
      </UFormField>
    </template>

    <template #footer>
      <UButton class="justify-center" :loading="saving" @click="onSave">
        保存
      </UButton>
      <UButton class="justify-center" color="neutral" variant="outline" @click="show = false">
        取消
      </UButton>
    </template>
  </UModal>
</template>
