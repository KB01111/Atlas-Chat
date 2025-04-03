// This file replaces the original connection.ts with a simplified version
// that removes direct LLM connection logic and only connects to our custom backend

import { useApi } from './simplified-api';

// Simplified connection handler that removes all direct LLM connection logic
export const useConnectionManager = () => {
  const api = useApi();
  
  // Return a simplified connection manager that only works with our backend
  return {
    // Simplified chat message handler
    sendChatMessage: async (agentId, message, history) => {
      try {
        // Use our API to send the message to the backend
        const stream = await api.sendChatMessage(agentId, message, history);
        return {
          success: true,
          stream: stream,
          error: null
        };
      } catch (error) {
        console.error('Error sending chat message:', error);
        return {
          success: false,
          stream: null,
          error: 'Failed to send message. Please try again.'
        };
      }
    },
    
    // Simplified connection status
    getConnectionStatus: () => {
      return {
        isConnected: true,
        endpoint: 'atlaschat',
        model: 'atlaschat',
        error: null
      };
    },
    
    // Stub for compatibility
    abortRequest: () => {
      console.log('Request aborted');
    }
  };
};

// Export a simplified connection handler for direct imports
export const connectionHandler = {
  sendChatMessage: async (agentId, message, history) => {
    const api = useApi();
    return api.sendChatMessage(agentId, message, history);
  },
  
  abortRequest: () => {
    console.log('Request aborted');
  }
};
