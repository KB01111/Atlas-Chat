// This file replaces the complex API routes with simplified versions
// that only connect to our custom backend

import { useApi } from './simplified-api';

// Simplified mutations that remove unnecessary API routes
export const mutations = {
  // Chat-related mutations
  useSendMessageMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async ({ agentId, message, history }) => {
        return api.sendChatMessage(agentId, message, history);
      },
      isLoading: false,
      error: null
    };
  },
  
  // Agent-related mutations
  useCreateAgentMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async (agent) => {
        return api.createAgent(agent);
      },
      isLoading: false,
      error: null
    };
  },
  
  useUpdateAgentMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async ({ agentId, agent }) => {
        return api.updateAgent(agentId, agent);
      },
      isLoading: false,
      error: null
    };
  },
  
  useDeleteAgentMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async (agentId) => {
        return api.deleteAgent(agentId);
      },
      isLoading: false,
      error: null
    };
  },
  
  // Auth-related mutations (simplified)
  useLoginUserMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async ({ email, password }) => {
        return api.login(email, password);
      },
      isLoading: false,
      error: null
    };
  },
  
  useRegisterUserMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async (userData) => {
        return api.register(userData);
      },
      isLoading: false,
      error: null
    };
  },
  
  useLogoutUserMutation: () => {
    const api = useApi();
    
    return {
      mutateAsync: async () => {
        return api.logout();
      },
      isLoading: false,
      error: null
    };
  },
  
  // Stubs for compatibility - these will be removed in future
  useUpdateConversationMutation: () => ({
    mutateAsync: async () => ({}),
    isLoading: false,
    error: null
  }),
  
  useDeleteConversationMutation: () => ({
    mutateAsync: async () => ({}),
    isLoading: false,
    error: null
  }),
  
  useUpdatePresetMutation: () => ({
    mutateAsync: async () => ({}),
    isLoading: false,
    error: null
  }),
  
  useCreatePresetMutation: () => ({
    mutateAsync: async () => ({}),
    isLoading: false,
    error: null
  }),
  
  useDeletePresetMutation: () => ({
    mutateAsync: async () => ({}),
    isLoading: false,
    error: null
  })
};

// Simplified queries that remove unnecessary API routes
export const queries = {
  // Agent-related queries
  useGetAgentsQuery: () => {
    const api = useApi();
    
    return {
      data: [],
      isLoading: true,
      isError: false,
      error: null,
      refetch: async () => {
        try {
          const agents = await api.getAgents();
          return { data: agents };
        } catch (error) {
          console.error('Error fetching agents:', error);
          return { data: [] };
        }
      }
    };
  },
  
  useGetAgentQuery: (agentId) => {
    const api = useApi();
    
    return {
      data: null,
      isLoading: true,
      isError: false,
      error: null,
      refetch: async () => {
        try {
          const agent = await api.getAgent(agentId);
          return { data: agent };
        } catch (error) {
          console.error(`Error fetching agent ${agentId}:`, error);
          return { data: null };
        }
      }
    };
  },
  
  // User-related queries
  useGetUserQuery: () => {
    const api = useApi();
    
    return {
      data: null,
      isLoading: true,
      isError: false,
      error: null,
      refetch: async () => {
        try {
          const user = await api.getCurrentUser();
          return { data: user };
        } catch (error) {
          console.error('Error fetching user:', error);
          return { data: null };
        }
      }
    };
  },
  
  // Stubs for compatibility - these will be removed in future
  useGetConversationsQuery: () => ({
    data: [],
    isLoading: false,
    isError: false,
    error: null,
    refetch: async () => ({ data: [] })
  }),
  
  useGetConversationByIdQuery: () => ({
    data: null,
    isLoading: false,
    isError: false,
    error: null,
    refetch: async () => ({ data: null })
  }),
  
  useGetPresetsQuery: () => ({
    data: [],
    isLoading: false,
    isError: false,
    error: null,
    refetch: async () => ({ data: [] })
  }),
  
  useGetSearchEnabledQuery: () => ({
    data: { isSearchEnabled: false },
    isLoading: false,
    isError: false,
    error: null
  }),
  
  useGetModelsQuery: () => ({
    data: { models: [] },
    isLoading: false,
    isError: false,
    error: null
  })
};

// Export simplified API routes
export default {
  mutations,
  queries
};
