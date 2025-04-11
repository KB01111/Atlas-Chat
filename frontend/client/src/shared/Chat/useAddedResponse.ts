import { useMemo } from 'react';

import useAddedHelpers from '~/hooks/Chat/useAddedHelpers';
import useGenerateConvo from '~/hooks/Conversations/useGenerateConvo';

export default function useAddedResponse({ rootIndex }: { rootIndex: number }) {
  const currentIndex = useMemo(() => rootIndex + 1, [rootIndex]);
  const {
    ask,
    regenerate,
    setMessages,
    getMessages,
    conversation,
    isSubmitting,
    setConversation,
    setIsSubmitting,
  } = useAddedHelpers({
    rootIndex,
    currentIndex,
  });

  const { generateConversation } = useGenerateConvo({
    index: currentIndex,
    rootIndex,
    setConversation,
  });

  return {
    ask,
    regenerate,
    getMessages,
    setMessages,
    conversation,
    isSubmitting,
    setConversation,
    setIsSubmitting,
    generateConversation,
    addedIndex: currentIndex,
  };
}
