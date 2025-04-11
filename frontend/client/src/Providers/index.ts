export const useToastContext = () => {
  return {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    showToast: (message: string) => {
      console.warn('showToast not implemented', message);
    },
  };
};
