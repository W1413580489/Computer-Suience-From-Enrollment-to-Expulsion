import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { router } from './router';
import '@/styles/tokens.css';
import '@/styles/hud.css';
import '@/styles/responsive.css';

/* zenless-ui 仿绝区零组件库 */
import ZenlessUI from 'zenless-ui';
import 'zenless-ui/dist/index.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ZenlessUI, { isBold: true });  /* 启用粗体 = 更贴近绝区零风格 */
app.mount('#app');
