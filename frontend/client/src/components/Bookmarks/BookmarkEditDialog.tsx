import * as React from 'react';
import { useRef } from 'react';
import OGDialogTemplate from '~/components/ui/OGDialogTemplate';
import { Button } from '~/components/ui/Button';
import { useConversationTagMutation } from 'librechat-data-provider';
import { Spinner } from '~/components';
import { OGDialog } from '~/components/ui/OriginalDialog';
import { NotificationSeverity } from '~/common';
import { useToastContext } from '~/Providers';
import BookmarkForm from './BookmarkForm';
import { useLocalize } from '~/hooks';
import { logger } from '~/utils';

import type { Bookmark } from './types';

interface BookmarkVars {
  addToConversation?: boolean;
  tag?: string;
}

type BookmarkEditDialogProps = {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  tags?: string[];
  setTags?: (tags: string[]) => void;
  context: string;
  bookmark?: Bookmark;
  conversationId?: string;
  children?: React.ReactNode;
  triggerRef?: React.RefObject<HTMLButtonElement>;
};

const BookmarkEditDialog = ({
  open,
  setOpen,
  tags,
  setTags,
  context,
  bookmark,
  children,
  triggerRef,
  conversationId,
}: BookmarkEditDialogProps) => {
  const localize = useLocalize();
  const formRef = useRef<HTMLFormElement>(null);

  const { showToast } = useToastContext();
  const mutation = useConversationTagMutation({
    context,
    tag: bookmark?.tag,
    options: {
      onSuccess: (_data: unknown, vars: BookmarkVars) => {
        showToast(
          bookmark
            ? localize('com_ui_bookmarks_update_success')
            : localize('com_ui_bookmarks_create_success')
        );
        setOpen(false);
        logger.log('tag_mutation', 'tags before setting', tags);

        if (setTags && vars.addToConversation === true) {
          const newTags = [...(tags || []), vars.tag].filter(
            (tag) => tag !== undefined,
          ) as string[];
          setTags(newTags);

          logger.log('tag_mutation', 'tags after', newTags);
          if (vars.tag == null || vars.tag === '') {
            return;
          }

          setTimeout(() => {
            const tagElement = document.getElementById(vars.tag ?? '');
            console.log('tagElement', tagElement);
            if (!tagElement) {
              return;
            }
            tagElement.focus();
          }, 5);
        }
      },
      onError: () => {
        showToast(
          bookmark
            ? localize('com_ui_bookmarks_update_error')
            : localize('com_ui_bookmarks_create_error')
        );
      },
    },
  });

  const handleSubmitForm = () => {
    if (formRef.current) {
      formRef.current.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
  };

  return (
    <OGDialog open={open} onOpenChange={setOpen} triggerRef={triggerRef}>
      {children}
      <OGDialogTemplate
        title="Bookmark"
        showCloseButton={false}
        className="w-11/12 md:max-w-2xl"
        main={
          <BookmarkForm
            tags={tags}
            setOpen={setOpen}
            mutation={mutation}
            conversationId={conversationId}
            bookmark={bookmark}
            formRef={formRef}
          />
        }
        buttons={
          <Button
            variant="submit"
            type="submit"
            disabled={mutation.isLoading}
            onClick={handleSubmitForm}
            className="text-white"
          >
            {mutation.isLoading ? <Spinner /> : localize('com_ui_save')}
          </Button>
        }
      />
    </OGDialog>
  );
};

export default BookmarkEditDialog;
