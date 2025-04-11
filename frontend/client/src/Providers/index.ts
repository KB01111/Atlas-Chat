export const useToastContext = () => {
  return {
    showToast: (arg: string | { message: string; severity: any }) => {
      if (typeof arg === 'string') {
        console.warn('showToast not implemented', arg);
      } else {
        console.warn('showToast not implemented', arg.message);
      }
    },
  };
};
