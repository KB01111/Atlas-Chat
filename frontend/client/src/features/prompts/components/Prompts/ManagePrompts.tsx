import { useCallback } from 'react';
import { useSetRecoilState } from 'recoil';

import { Button } from '~/components/ui';
import { useLocalize, useCustomLink } from '~/hooks';
import store from '~/store';
import { cn } from '~/utils';

export default function ManagePrompts({ className }: { className?: string }) {
  const localize = useLocalize();
  const setPromptsName = useSetRecoilState(store.promptsName);
  const setPromptsCategory = useSetRecoilState(store.promptsCategory);
  const clickCallback = useCallback(() => {
    setPromptsName('');
    setPromptsCategory('');
  }, [setPromptsName, setPromptsCategory]);

  const customLink = useCustomLink('/d/prompts', clickCallback);
  const clickHandler = (e: React.MouseEvent<HTMLButtonElement>) => {
    customLink(e as unknown as React.MouseEvent<HTMLAnchorElement>);
  };

  return (
    <Button
      variant="outline"
      className={cn(className, 'bg-transparent')}
      onClick={clickHandler}
      aria-label="Manage Prompts"
      role="button"
    >
      {localize('com_ui_manage')}
    </Button>
  );
}
