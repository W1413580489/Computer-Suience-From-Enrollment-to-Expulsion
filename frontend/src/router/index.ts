import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/guides', name: 'guides', component: () => import('@/views/GuidesView.vue') },
  { path: '/appendix', name: 'appendix', component: () => import('@/views/AppendixView.vue') },
  { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue') },
  { path: '/changelog', name: 'changelog', component: () => import('@/views/ChangelogView.vue') },
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
