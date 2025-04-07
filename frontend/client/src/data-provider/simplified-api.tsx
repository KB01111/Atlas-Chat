import { createContext, type ReactNode, useContext, useState } from "react";

// Define types for our context
interface ApiContextType {
  baseUrl: string;
  getAgents: () => Promise<any[]>;
  getAgent: (agentId: string) => Promise<any>;
  createAgent: (agent: any) => Promise<any>;
  updateAgent: (agentId: string, agent: any) => Promise<any>;
  deleteAgent: (agentId: string) => Promise<void>;
  sendChatMessage: (
    agentId: string,
    message: string,
    history: any[],
  ) => Promise<ReadableStream<Uint8Array> | null>;
  login: (email: string, password: string) => Promise<any>;
  register: (userData: any) => Promise<any>;
  logout: () => Promise<void>;
  getCurrentUser: () => Promise<any>;
}

// Create context with default values
const ApiContext = createContext<ApiContextType>({
  baseUrl: "http://localhost:8000",
  getAgents: async () => [],
  getAgent: async () => ({}),
  createAgent: async () => ({}),
  updateAgent: async () => ({}),
  deleteAgent: async () => {},
  sendChatMessage: async () => null,
  login: async () => ({}),
  register: async () => ({}),
  logout: async () => {},
  getCurrentUser: async () => ({}),
});

// Provider component
export const ApiProvider = ({ children }: { children: ReactNode }) => {
  const [baseUrl, setBaseUrl] = useState("http://localhost:8000");

  // Get JWT token from localStorage
  const getToken = () => localStorage.getItem("auth_token");

  // Headers with authentication
  const getHeaders = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  });

  // API functions
  const getAgents = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/agents`, {
        method: "GET",
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Error fetching agents: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching agents:", error);
      return [];
    }
  };

  const getAgent = async (agentId: string) => {
    try {
      const response = await fetch(`${baseUrl}/api/agents/${agentId}`, {
        method: "GET",
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Error fetching agent: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error fetching agent ${agentId}:`, error);
      return {};
    }
  };

  const createAgent = async (agent: any) => {
    try {
      const response = await fetch(`${baseUrl}/api/agents`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(agent),
      });

      if (!response.ok) {
        throw new Error(`Error creating agent: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error creating agent:", error);
      throw error;
    }
  };

  const updateAgent = async (agentId: string, agent: any) => {
    try {
      const response = await fetch(`${baseUrl}/api/agents/${agentId}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(agent),
      });

      if (!response.ok) {
        throw new Error(`Error updating agent: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error updating agent ${agentId}:`, error);
      throw error;
    }
  };

  const deleteAgent = async (agentId: string) => {
    try {
      const response = await fetch(`${baseUrl}/api/agents/${agentId}`, {
        method: "DELETE",
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Error deleting agent: ${response.statusText}`);
      }
    } catch (error) {
      console.error(`Error deleting agent ${agentId}:`, error);
      throw error;
    }
  };

  const sendChatMessage = async (agentId: string, message: string, history: any[]) => {
    try {
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({
          agent_id: agentId,
          message,
          history,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error sending chat message: ${response.statusText}`);
      }

      return response.body;
    } catch (error) {
      console.error("Error sending chat message:", error);
      return null;
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${baseUrl}/api/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: email, // API expects username field but we use email
          password,
        }),
      });

      if (!response.ok) {
        throw new Error(`Login failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Store token in localStorage
      localStorage.setItem("auth_token", data.access_token);

      return data;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      const response = await fetch(`${baseUrl}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error(`Registration failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Remove token from localStorage
      localStorage.removeItem("auth_token");

      // No need to call backend for logout as we're using JWT
      // If needed in the future, uncomment:
      // await fetch(`${baseUrl}/api/auth/logout`, {
      //   method: 'POST',
      //   headers: getHeaders(),
      // });
    } catch (error) {
      console.error("Logout error:", error);
      throw error;
    }
  };

  const getCurrentUser = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/auth/me`, {
        method: "GET",
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Error fetching user: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  };

  // Context value
  const value = {
    baseUrl,
    getAgents,
    getAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    sendChatMessage,
    login,
    register,
    logout,
    getCurrentUser,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

// Custom hook to use the API context
export const useApi = () => useContext(ApiContext);

// Export a simplified data service that can be used as a drop-in replacement
// for the existing LibreChat data service
export const dataService = {
  // Agent definitions
  getAgents: () => useApi().getAgents(),
  getAgent: (agentId: string) => useApi().getAgent(agentId),
  createAgent: (agent: any) => useApi().createAgent(agent),
  updateAgent: (agentId: string, agent: any) => useApi().updateAgent(agentId, agent),
  deleteAgent: (agentId: string) => useApi().deleteAgent(agentId),

  // Chat
  sendChatMessage: (agentId: string, message: string, history: any[]) =>
    useApi().sendChatMessage(agentId, message, history),

  // Auth
  login: (credentials: { email: string; password: string }) =>
    useApi().login(credentials.email, credentials.password),
  register: (userData: any) => useApi().register(userData),
  logout: () => useApi().logout(),
  getCurrentUser: () => useApi().getCurrentUser(),

  // Stubs for LibreChat compatibility - these will be removed in future
  getAIEndpoints: () => Promise.resolve({ endpoints: [] }),
  getStartupConfig: () => Promise.resolve({ appTitle: "AtlasChat" }),
};
