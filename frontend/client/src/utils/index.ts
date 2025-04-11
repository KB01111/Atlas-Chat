/* eslint-disable @typescript-eslint/no-explicit-any */
export const logger = {
  log: (...args: any[]) => {
    console.log('LOG:', ...args);
  },
  info: (...args: any[]) => {
    console.info('INFO:', ...args);
  },
  warn: (...args: any[]) => {
    console.warn('WARN:', ...args);
  },
  error: (...args: any[]) => {
    console.error('ERROR:', ...args);
  },
};

export const detectVariables = (input: string): string[] => {
  const regex = /{{\s*([^{}\s]+)\s*}}/g;
  const matches = [...input.matchAll(regex)];
  return matches.map((match) => match[1]);
};

export const cn = (...args: any[]): string => {
  return args.filter(Boolean).join(' ');
};

export function addFileToCache(queryClient: any, file: any): void {
  console.warn('[Stub] addFileToCache called but not implemented', file);
}

// Add other missing utility functions if needed - ensure correct export syntax
export const getEndpoint = (): string => 'mock_endpoint';
export const getIcon = (): string => 'mock_icon';
export const getAssistantsMap = (): Record<string, unknown> => ({});
export const findPromptGroup = (data: any, predicate: any): any => null;
export const getPromptGroupLabel = (group: any): string => group?.name || 'Unknown Group';
export const getCategory = (category: string): string => category;
export const defaultTextProps = {};
export const parseAndDisplayVariables = (text: string): string => text;
export const getAssistantName = (assistant: any): string => assistant?.name || 'Unknown Assistant';
export const getAssistantAvatar = (assistant: any): string => '';
export const getModelSpecIconURL = (spec: any): string => '';
export const getPresetTitle = (preset: any): string => preset?.title || 'Untitled';
export const getSender = (message: any): string => message?.sender || 'Unknown';
export const parseVariable = (variable: string): string => variable;
export const stringToHex = (str: string): string => ''; // Placeholder
export const getIconEndpoint = (endpoint: string): string => endpoint;
export const getIconClass = (icon: string): string => icon;
export const getPluginAuthValue = (value: string): string => value;
export const getPluginName = (plugin: any): string => plugin?.name || 'Unknown Plugin';
export const convoSchema = {}; // Assuming this should be an object
export const getEndpointType = (): string => 'mock_type';
export const getTextContentType = (text: string): string => 'text';
export const supportsFiles = (endpoint: string): boolean => false;
export const isMacOS = (): boolean => false;
export const findMention = (text: string): any => null; // Add missing function
export const parseCompact = (json: string): any => JSON.parse(json); // Add missing function
export const getPromptById = (id: string): any => null; // Add missing function
export const mapVariable = (key: string, value: string, prompt: string): string => prompt; // Add missing function
export const removeVariable = (key: string, prompt: string): string => prompt; // Add missing function
export const replaceVariable = (variable: string, value: string, prompt: string): string => prompt; // Add missing function
