export const useLocalize = () => {
  return (key: string) => key;
};

export const useSubmitMessage = () => {
  return {
    submit: (message: string) => {},
    submitPrompt: (prompt: string) => {},
    isLoading: false,
    error: null,
  };
};

export const useCustomLink = <T = any>(url: string) => {
  return (e?: any) => {};
};

export const useAuthContext = () => {
  return {
    user: { id: '', role: '' },
    login: () => {},
    logout: () => {},
  };
};
