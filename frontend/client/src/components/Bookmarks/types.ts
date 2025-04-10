export interface TConversationTagRequest {
  tag: string;
  description: string;
  conversationId: string;
  addToConversation: boolean;
}

export interface Bookmark {
  tag: string;
  description?: string;
  // Add other properties as needed
}