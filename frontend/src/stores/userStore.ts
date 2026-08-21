import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export type Grade = 1 | 2 | 3 | 4;
export type MajorCategory = 'software' | 'hardware' | 'other';

export interface UserProfile {
  nickname: string;
  grade: Grade;
  major: MajorCategory;
  avatar?: string;       // base64 图片数据
  uid: string;           // 唯一编号 XKZ-YYYYMMDD-XXXX
  createdAt: string;     // 建号日期 YYYY-MM-DD
}

function generateUid(): string {
  const d = new Date();
  const ymd = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  const rand = Math.random().toString(16).slice(2, 6).toUpperCase();
  return `XKZ-${ymd}-${rand}`;
}

function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
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

  function login(data: Omit<UserProfile, 'uid' | 'createdAt'> & Partial<Pick<UserProfile, 'uid' | 'createdAt'>>) {
    user.value = {
      ...data,
      uid: data.uid ?? generateUid(),
      createdAt: data.createdAt ?? todayStr(),
    };
    localStorage.setItem('xkz_user', JSON.stringify(user.value));
  }

  function logout() {
    user.value = null;
    localStorage.removeItem('xkz_user');
  }

  function updateAvatar(base64: string) {
    if (user.value) {
      user.value.avatar = base64;
      localStorage.setItem('xkz_user', JSON.stringify(user.value));
    }
  }

  return { user, isLoggedIn, gradeLabel, majorLabel, isSoftware, login, logout, updateAvatar };
});
