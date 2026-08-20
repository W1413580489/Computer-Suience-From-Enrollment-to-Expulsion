import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/guides', name: 'guides', component: () => import('@/views/GuidesView.vue') },
  { path: '/appendix', name: 'appendix', component: () => import('@/views/AppendixView.vue') },
  { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue') },
  { path: '/changelog', name: 'changelog', component: () => import('@/views/ChangelogView.vue') },
  { path: '/glossary', name: 'glossary', component: () => import('@/views/GlossaryView.vue') },
  { path: '/quest', name: 'quest', component: () => import('@/views/QuestView.vue') },
  { path: '/resources', name: 'resources', component: () => import('@/views/ResourceView.vue') },
  { path: '/calendar', name: 'calendar', component: () => import('@/views/CalendarView.vue') },
  { path: '/chat', name: 'chat', component: () => import('@/views/ChatView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 登录守卫：未登录访问首页 → 跳转登录页（游客模式除外）
router.beforeEach((to) => {
  // 登录页不检查
  if (to.name === 'login') return true;

  const userStore = useUserStore();

  // 未登录时访问首页 → 跳转登录页
  // 带 ?guest=1 的请求视为游客模式，允许通过
  if (to.path === '/' && !userStore.isLoggedIn && to.query.guest !== '1') {
    return { name: 'login' };
  }

  return true;
});
