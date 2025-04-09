export const useGetBannerQuery = () => {
  return {
    data: { bannerId: '', message: '' },
    isLoading: false,
    error: null,
  };
};

export const useDeletePromptGroup = (options?: any) => {
  return {
    mutate: (payload?: any) => {},
    isLoading: false,
    error: null,
  };
};

export const useUpdatePromptGroup = (options?: any) => {
  return {
    mutate: (payload?: any) => {},
    isLoading: false,
    error: null,
  };
};

export const useConversationTagMutation = (options?: any) => {
  return {
    mutate: (payload?: any) => {},
    isLoading: false,
    error: null,
  };
};