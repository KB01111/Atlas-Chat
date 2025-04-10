export const logger = {
  log: (...args: any[]) => {},
  info: (...args: any[]) => {},
  warn: (...args: any[]) => {},
  error: (...args: any[]) => {},
};

export const detectVariables = (input: string) => {
  return [];
};

export const cn = (...args: any[]) => {
  return args.filter(Boolean).join(' ');
};

export function addFileToCache(queryClient: any, file: any) {
  console.warn('[Stub] addFileToCache called but not implemented', file);
}
