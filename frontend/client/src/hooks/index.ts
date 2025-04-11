/* eslint-disable @typescript-eslint/no-unused-vars */
export const useLocalize = () => {
  return (key: string) => key;
};

export const useSubmitMessage = () => {
  return {
    submit: (message: string) => {
      console.warn('submit not implemented', message);
    },
    submitPrompt: (prompt: string) => {
      console.warn('submitPrompt not implemented', prompt);
    },
    isLoading: false,
    error: null,
  };
};

export const useCustomLink = <T = any>(url: string) => {
  return (e?: any) => {
    console.warn('useCustomLink handler not implemented', url, e);
  };
};

export const useAuthContext = () => {
  return {
    user: { id: 'test-user', role: 'user' }, // Provide some default mock data
    login: () => {
      console.warn('login not implemented');
    },
    logout: () => {
      console.warn('logout not implemented');
    },
  };
};
