import { useCallback, useState } from 'react';
import type { FC } from 'react';

import { NotificationSeverity } from '~/common';
import { TrashIcon } from '~/components/svg';
import { Label, OGDialog, OGDialogTrigger, TooltipAnchor } from '~/components/ui';
import OGDialogTemplate from '~/components/ui/OGDialogTemplate';
import { useConversationTagMutation } from '~/data-provider';
import { useLocalize } from '~/hooks';
import { useToastContext } from '~/Providers';

const DeleteBookmarkButton: FC<{
  bookmark: string;
  tabIndex?: number;
  onFocus?: () => void;
  onBlur?: () => void;
}> = ({ bookmark, tabIndex = 0, onFocus, onBlur }) => {
  const localize = useLocalize();
  const { showToast } = useToastContext();
  const [open, setOpen] = useState(false);

  const deleteBookmarkMutation = useConversationTagMutation({
    onSuccess: () => {
      showToast(localize('com_ui_bookmarks_delete_success'));
    },
    onError: () => {
      showToast({
        message: localize('com_ui_bookmarks_delete_error'),
        severity: NotificationSeverity.Error,
      });
    },
  });

  const confirmDelete = useCallback(async () => {
    deleteBookmarkMutation.mutate(bookmark);
  }, [bookmark, deleteBookmarkMutation]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      event.stopPropagation();
      setOpen(!open);
    }
  };

  return (
    <>
      <OGDialog open={open} onOpenChange={setOpen}>
        <OGDialogTrigger asChild>
          <TooltipAnchor
            role="button"
            aria-label={localize('com_ui_bookmarks_delete')}
            description={localize('com_ui_delete')}
            className="flex size-7 items-center justify-center rounded-lg transition-colors duration-200 hover:bg-surface-hover"
          />
        </OGDialogTrigger>
        <OGDialogTemplate
          showCloseButton={false}
          title={localize('com_ui_bookmarks_delete')}
          className="w-11/12 max-w-lg"
          main={
            <Label className="text-left text-sm font-medium">
              {localize('com_ui_bookmark_delete_confirm')} {bookmark}
            </Label>
          }
          selection={{
            selectHandler: confirmDelete,
            selectClasses:
              'bg-red-700 dark:bg-red-600 hover:bg-red-800 dark:hover:bg-red-800 text-white',
            selectText: localize('com_ui_delete'),
          }}
        />
      </OGDialog>
    </>
  );
};

export default DeleteBookmarkButton;
