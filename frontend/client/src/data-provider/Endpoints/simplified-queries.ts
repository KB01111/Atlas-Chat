// This file replaces the original Endpoints directory with a simplified version
// that only supports our custom backend

import { useApi } from '../simplified-api';

// Export a simplified version that maintains API compatibility
// but removes all the multi-endpoint configuration logic
export const useGetEndpointsQuery = () => {
  // Return a fixed response with only our custom backend
  return {
    data: {
      endpoints: [
        {
          id: 'atlaschat',
          name: 'AtlasChat',
          endpoint: 'atlaschat',
          description: 'Custom AtlasChat backend',
          isDefault: true
        }
      ]
    },
    isLoading: false,
    isError: false,
    error: null
  };
};

// Simplified version of the startup config query
export const useGetStartupConfig = () => {
  return {
    data: {
      appTitle: 'AtlasChat',
      defaultEndpoint: 'atlaschat',
      defaultModel: 'atlaschat',
      showModelSettings: false
    },
    isLoading: false,
    isError: false,
    error: null
  };
};
