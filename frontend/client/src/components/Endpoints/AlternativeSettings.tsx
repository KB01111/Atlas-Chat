import { SettingsViews } from 'librechat-data-provider';
import { useRecoilValue } from 'recoil';

import type { TSettingsProps } from '~/common';
import store from '~/store';
import { cn } from '~/utils';

import { Advanced } from './Settings';

export default function AlternativeSettings({
  conversation,
  setOption,
  isPreset = false,
  className = '',
}: TSettingsProps) {
  const currentSettingsView = useRecoilValue(store.currentSettingsView);
  if (!conversation?.endpoint || currentSettingsView === SettingsViews.default) {
    return null;
  }

  return (
    <div className={cn('hide-scrollbar h-[500px] overflow-y-auto md:mb-2 md:h-[350px]', className)}>
      <Advanced conversation={conversation} setOption={setOption} isPreset={isPreset} />
    </div>
  );
}
