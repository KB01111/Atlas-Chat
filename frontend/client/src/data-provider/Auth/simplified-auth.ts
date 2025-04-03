// This file replaces the complex Auth directory with simplified versions
// that only support basic JWT authentication

import { useApi } from '../simplified-api';

// Simplified auth mutations
export const mutations = {
  // Login mutation
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
  
  // Register mutation
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
  
  // Logout mutation
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
  
  // Remove all 2FA related mutations
  useEnableTwoFactorMutation: null,
  useVerifyTwoFactorMutation: null,
  useConfirmTwoFactorMutation: null,
  useDisableTwoFactorMutation: null,
  useRegenerateBackupCodesMutation: null,
  useVerifyTwoFactorTempMutation: null
};

// Simplified auth queries
export const queries = {
  // Get current user query
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
  
  // Remove all 2FA related queries
  useGet2FAStatusQuery: null
};

// Export simplified auth
export default {
  mutations,
  queries
};
