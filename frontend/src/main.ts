import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { router } from './router';
import { useBgImage } from '@/composables/useBgImage';
import '@/styles/tokens.css';
import '@/styles/hud.css';
import '@/styles/responsive.css';

/* 应用启动即恢复自定义背景（读写 IndexedDB）。
   必须在入口执行：此前初始化只挂在设置面板组件里，直接刷新到
   非首页路由（攻略/教学等）时 init 从未运行，背景必然丢失。 */
useBgImage();

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ZenlessUI, { isBold: true });  /* 启用粗体 = 更贴近绝区零风格 */
app.mount('#app');
