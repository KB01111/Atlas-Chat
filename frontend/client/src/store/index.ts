import { atom } from 'recoil';

export const dummyState = atom({
  key: 'dummyState',
  default: null,
});

export const hideBannerHint = atom<string[]>({
  key: 'hideBannerHint',
  default: [],
});

const store = {
  hideBannerHint,
};

export default store;