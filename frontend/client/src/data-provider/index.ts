/* eslint-disable @typescript-eslint/no-unused-vars */
export const useGetBannerQuery = () => {
  return {
    data: { bannerId: '', message: '' },
    isLoading: false,
    error: null,
  };
};

export const useDeletePromptGroup = (options?: any) => {
  return {
    mutate: (payload?: any) => {
      console.warn('useDeletePromptGroup mutation not implemented', payload);
    },
    isLoading: false,
    error: null,
  };
};

export const useUpdatePromptGroup = (options?: any) => {
  return {
    mutate: (payload?: any) => {
      console.warn('useUpdatePromptGroup mutation not implemented', payload);
    },
    isLoading: false,
    error: null,
  };
};

export const useConversationTagMutation = (options?: any) => {
  return {
    mutate: (payload?: any) => {
      console.warn('useConversationTagMutation mutation not implemented', payload);
    },
    isLoading: false,
    error: null,
  };
};
