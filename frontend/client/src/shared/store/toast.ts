import { atom } from 'recoil';

import { NotificationSeverity } from '~/common';

const toastState = atom({
  key: 'toastState',
  default: {
    open: false,
    message: '',
    severity: NotificationSeverity.Success,
    showIcon: true,
  },
});

export default { toastState };
