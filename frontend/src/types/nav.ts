export interface SideMenuItem {
  key: string;
  label: string;
  subLabel: string;
  number: string;
  route: string;
  icon: string;
}

export interface GuideItem {
  label: string;
  desc?: string;
  url: string;
  icon?: string;
}

export interface AppendixItem extends GuideItem {
  restricted?: boolean;
}

export interface QuickAccessItem {
  label: string;
  desc: string;
  url: string;
}

export interface FooterToolItem {
  label: string;
  url: string;
}

export interface MobileTab {
  key: string;
  label: string;
  subLabel: string;
  icon: string;
  route: string;
}

export interface ChangelogEntry {
  version: string;
  date: string;
  changes: string[];
}

export interface Citation {
  id: number;
  title: string;
  url: string;
  excerpt?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  qHash?: string;
  feedback?: 'up' | 'down' | null;
  error?: string;
  streaming?: boolean;
}
