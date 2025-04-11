import type { TUser, TPlugin } from 'librechat-data-provider';
import { atom } from 'recoil';

const user = atom<TUser | undefined>({
  key: 'user',
  default: undefined,
});

const availableTools = atom<Record<string, TPlugin>>({
  key: 'availableTools',
  default: {},
});

export default {
  user,
  availableTools,
};
