// navStore：启动时从后端加载 nav_config / changelog，缓存至 Pinia（§8.8.4）
import { defineStore } from 'pinia';
import type {
  SideMenuItem,
  GuideItem,
  AppendixItem,
  QuickAccessItem,
  FooterToolItem,
  ChangelogEntry,
} from '@/types/nav';

interface NavState {
  sideMenu: SideMenuItem[];
  guides: GuideItem[];
  appendix: AppendixItem[];
  quickAccess: QuickAccessItem[];
  footerTools: FooterToolItem[];
  slogan: { main: string; sub: string };
  systemIndicator: { label: string; version: string };
  chatRoute: string;
  changelog: ChangelogEntry[];
  loaded: boolean;
  loadError: string;
}

export const useNavStore = defineStore('nav', {
  state: (): NavState => ({
    sideMenu: [],
    guides: [],
    appendix: [],
    quickAccess: [],
    footerTools: [],
    slogan: { main: '', sub: '' },
    systemIndicator: { label: '', version: '' },
    chatRoute: '/chat',
    changelog: [],
    loaded: false,
    loadError: '',
  }),
  actions: {
    async load() {
      try {
        const [cfgRes, chgRes] = await Promise.all([
          fetch('/api/nav_config'),
          fetch('/api/changelog'),
        ]);
        if (!cfgRes.ok) throw new Error(`nav_config HTTP ${cfgRes.status}`);
        const cfg = await cfgRes.json();
        this.sideMenu = cfg.sideMenu ?? [];
        this.guides = cfg.guides ?? [];
        this.appendix = cfg.appendix ?? [];
        this.quickAccess = cfg.quickAccess ?? [];
        this.footerTools = cfg.footerTools ?? [];
        this.slogan = cfg.slogan ?? { main: '', sub: '' };
        this.systemIndicator = cfg.systemIndicator ?? { label: '', version: '' };
        this.chatRoute = cfg.chat ?? '/chat';
        if (chgRes.ok) this.changelog = (await chgRes.json()).data ?? [];
        this.loaded = true;
      } catch (e) {
        this.loadError = e instanceof Error ? e.message : '配置加载失败';
      }
    },
  },
});
