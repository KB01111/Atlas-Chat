export const useToastContext = () => {
  return {
    showToast: (arg: string | { message: string; severity: any }) => {},
  };
};
