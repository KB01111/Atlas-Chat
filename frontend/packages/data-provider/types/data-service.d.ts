import * as t from "./types";
export declare function getConversations(
  pageNumber: string,
): Promise<t.TGetConversationsResponse>;
export declare function abortRequestWithMessage(
  endpoint: string,
  abortKey: string,
  message: string,
): Promise<void>;
export declare function deleteConversation(
  payload: t.TDeleteConversationRequest,
): Promise<any>;
export declare function clearAllConversations(): Promise<unknown>;
export declare function getMessagesByConvoId(id: string): Promise<t.TMessage[]>;
export declare function getConversationById(
  id: string,
): Promise<t.TConversation>;
export declare function updateConversation(
  payload: t.TUpdateConversationRequest,
): Promise<t.TUpdateConversationResponse>;
export declare function getPresets(): Promise<t.TPreset[]>;
export declare function createPreset(payload: t.TPreset): Promise<t.TPreset[]>;
export declare function updatePreset(payload: t.TPreset): Promise<t.TPreset[]>;
export declare function deletePreset(
  arg: t.TPreset | object,
): Promise<t.TPreset[]>;
export declare function getSearchEnabled(): Promise<boolean>;
export declare function getUser(): Promise<t.TUser>;
export declare const searchConversations: (
  q: string,
  pageNumber: string,
) => Promise<t.TSearchResults>;
export declare const getAIEndpoints: () => Promise<unknown>;
export declare const updateTokenCount: (text: string) => Promise<any>;
export declare const login: (payload: t.TLoginUser) => Promise<any>;
export declare const logout: () => Promise<any>;
export declare const register: (payload: t.TRegisterUser) => Promise<any>;
export declare const refreshToken: () => Promise<any>;
export declare const getLoginGoogle: () => Promise<unknown>;
export declare const requestPasswordReset: (
  payload: t.TRequestPasswordReset,
) => Promise<t.TRequestPasswordResetResponse>;
export declare const resetPassword: (payload: t.TResetPassword) => Promise<any>;
export declare const getAvailablePlugins: () => Promise<t.TPlugin[]>;
export declare const updateUserPlugins: (
  payload: t.TUpdateUserPlugins,
) => Promise<any>;
export declare const getStartupConfig: () => Promise<t.TStartupConfig>;
