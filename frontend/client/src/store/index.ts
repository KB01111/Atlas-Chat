import { atom } from 'recoil';

export const dummyState = atom({
  key: 'dummyState',
  default: null,
});

export const hideBannerHint = atom<string[]>({
  key: 'hideBannerHint',
  default: [],
});

export const defaultPreset = atom<any>({
  key: 'defaultPreset',
  default: null,
});

export const presetModalVisible = atom<boolean>({
  key: 'presetModalVisible',
  default: false,
});

export const modularChat = atom<any>({
  key: 'modularChat',
  default: null,
});

export const plugins = atom<any[]>({
  key: 'plugins',
  default: [],
});

const store = {
  hideBannerHint,
  defaultPreset,
  presetModalVisible,
  modularChat,
  plugins,
};

export default store;
