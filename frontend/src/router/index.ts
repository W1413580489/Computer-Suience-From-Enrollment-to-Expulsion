import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import { useAchievementStore } from '@/stores/achievementStore';

const TRACK_PAGES = ['guides', 'appendix', 'about', 'changelog', 'glossary', 'resources', 'calendar', 'chat'];

const routes = [
  { path: '/splash', name: 'splash', component: () => import('@/components/login/SplashScreen.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/guides', name: 'guides', component: () => import('@/views/GuidesView.vue') },
  { path: '/appendix', name: 'appendix', component: () => import('@/views/AppendixView.vue') },
  { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue') },
  { path: '/changelog', name: 'changelog', component: () => import('@/views/ChangelogView.vue') },
  { path: '/glossary', name: 'glossary', component: () => import('@/views/GlossaryView.vue') },
  { path: '/quest', name: 'quest', component: () => import('@/views/QuestView.vue') },
  { path: '/roadmap', name: 'roadmap', component: () => import('@/views/RoadmapView.vue') },
  { path: '/teach', name: 'teach', component: () => import('@/views/TeachView.vue') },
  { path: '/resources', name: 'resources', component: () => import('@/views/ResourceView.vue') },
  { path: '/calendar', name: 'calendar', component: () => import('@/views/CalendarView.vue') },
  { path: '/chat', name: 'chat', component: () => import('@/views/ChatView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 开屏 / 建号 守卫
router.beforeEach((to) => {
  const userStore = useUserStore();

  // 已登录用户访问开屏/建号页 → 直接进入主页
  if ((to.name === 'splash' || to.name === 'login') && userStore.isLoggedIn) {
    return { name: 'home' };
  }

  // 开屏页和建号页无需登录
  if (to.name === 'splash' || to.name === 'login') return true;

  // 未登录时访问首页 → 跳转开屏页（游客模式除外）
  if (to.path === '/' && !userStore.isLoggedIn && to.query.guest !== '1') {
    return { name: 'splash' };
  }

  return true;
});

// 成就：页面访问追踪
router.afterEach((to) => {
  const ach = useAchievementStore();

  // 成就：首次访问更新日志
  if (to.name === 'changelog') {
    ach.unlock('view_changelog');
  }

  // 成就：访问过全部 8 个页面
  if (TRACK_PAGES.includes(to.name as string)) {
    try {
      const raw = localStorage.getItem('xkz_visited_pages');
      const visited: string[] = raw ? JSON.parse(raw) : [];
      if (!visited.includes(to.name as string)) {
        visited.push(to.name as string);
        localStorage.setItem('xkz_visited_pages', JSON.stringify(visited));
      }
      if (visited.length >= TRACK_PAGES.length) {
        ach.unlock('understand_all');
      }
    } catch {
      // ignore
    }
  }
});
