import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { router } from './router';
import { useBgImage } from '@/composables/useBgImage';
import ZenlessUIPlugin from 'zenless-ui';
import 'zenless-ui/dist/index.css';
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
/* 绑定名不要用 ZenlessUI——曾因此掩盖"import 丢失"的问题（esbuild
   不做类型检查，未导入的标识符被当成全局变量，运行时白屏） */
app.use(ZenlessUIPlugin, { isBold: true });  /* 启用粗体 = 更贴近绝区零风格 */
app.mount('#app');
