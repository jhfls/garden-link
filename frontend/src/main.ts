import ui from '@nuxt/ui/vue-plugin';
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { routes } from 'vue-router/auto-routes';
import App from './app.vue';
import './main.css';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

createApp(App)
  .use(router)
  .use(ui)
  .mount('#app')
;
