import { atomWithLocalStorage } from './utils';

const isTemporary = atomWithLocalStorage('isTemporary', false);

export default {
  isTemporary,
};
