<script setup lang="ts">
import { ref } from 'vue';

const showSettings = ref(false);

const onSettingsSave = () => window.location.reload();
</script>

<template>
  <UApp>
    <div class="fixed top-4 right-4 z-50">
      <UButton color="neutral" variant="ghost" icon="i-heroicons-cog-6-tooth" @click="showSettings = true" />
    </div>
    <RouterView />
    <SettingsDialog v-model:show="showSettings" @save="onSettingsSave" />
  </UApp>
</template>
