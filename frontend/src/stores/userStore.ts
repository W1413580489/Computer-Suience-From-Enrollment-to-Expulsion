import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export type Grade = 1 | 2 | 3 | 4;
export type MajorCategory = 'software' | 'hardware' | 'other';

export interface UserProfile {
  nickname: string;
  grade: Grade;
  major: MajorCategory;
}

export const useUserStore = defineStore('user', () => {
  const user = ref<UserProfile | null>(null);

  // 从 localStorage 恢复
  const stored = localStorage.getItem('xkz_user');
  if (stored) {
    try {
      user.value = JSON.parse(stored);
    } catch {
      /* ignore corrupt data */
    }
  }

  const isLoggedIn = computed(() => user.value !== null);

  const gradeLabel = computed(() => {
    if (!user.value) return '';
    return { 1: '大一', 2: '大二', 3: '大三', 4: '大四' }[user.value.grade];
  });

  const majorLabel = computed(() => {
    if (!user.value) return '';
    return { software: '软件类', hardware: '硬件类', other: '其他类' }[user.value.major];
  });

  const isSoftware = computed(() => user.value?.major === 'software');

  function login(data: UserProfile) {
    user.value = data;
    localStorage.setItem('xkz_user', JSON.stringify(data));
  }

  function logout() {
    user.value = null;
    localStorage.removeItem('xkz_user');
  }

  return { user, isLoggedIn, gradeLabel, majorLabel, isSoftware, login, logout };
});