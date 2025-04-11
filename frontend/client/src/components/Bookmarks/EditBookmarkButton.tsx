import { useState } from 'react';
import type { FC } from 'react';

import { EditIcon } from '~/components/svg';
import { TooltipAnchor, OGDialogTrigger } from '~/components/ui';
import { useLocalize } from '~/hooks';

import BookmarkEditDialog from './BookmarkEditDialog';
import type { Bookmark } from './types';

const EditBookmarkButton: FC<{
  bookmark: Bookmark;
  tabIndex?: number;
  onFocus?: () => void;
  onBlur?: () => void;
}> = ({
  bookmark,
  tabIndex = 0,
  onFocus,
  onBlur,
}: {
  bookmark: Bookmark;
  tabIndex?: number;
  onFocus?: () => void;
  onBlur?: () => void;
}) => {
  const localize = useLocalize();
  const [open, setOpen] = useState(false);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      setOpen(!open);
    }
  };

  return (
    <BookmarkEditDialog
      context="EditBookmarkButton"
      bookmark={bookmark}
      open={open}
      setOpen={setOpen}
    >
      <OGDialogTrigger asChild>
        <TooltipAnchor
          role="button"
          aria-label={localize('com_ui_bookmarks_edit')}
          description={localize('com_ui_edit')}
          tabIndex={tabIndex}
          onFocus={onFocus}
          onBlur={onBlur}
          onClick={() => setOpen(!open)}
          className="flex size-7 items-center justify-center rounded-lg transition-colors duration-200 hover:bg-surface-hover"
          onKeyDown={handleKeyDown}
        >
          <EditIcon />
        </TooltipAnchor>
      </OGDialogTrigger>
    </BookmarkEditDialog>
  );
};

export default EditBookmarkButton;
