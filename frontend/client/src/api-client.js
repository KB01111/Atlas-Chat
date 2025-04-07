import axios from "axios";

// Create API client with default configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("atlaschat_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("atlaschat_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// API functions for authentication
export const authAPI = {
  login: async (email, password) => {
    try {
      const response = await apiClient.post("/api/auth/login", {
        email,
        password,
      });
      localStorage.setItem("atlaschat_token", response.data.access_token);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Login failed" };
    }
  },

  register: async (name, email, password) => {
    try {
      const response = await apiClient.post("/api/auth/register", {
        name,
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Registration failed" };
    }
  },

  logout: () => {
    localStorage.removeItem("atlaschat_token");
  },

  getCurrentUser: async () => {
    try {
      const response = await apiClient.get("/api/auth/me");
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to get user data" };
    }
  },
};

// API functions for chat
export const chatAPI = {
  sendMessage: async (agentId, message, history) => {
    try {
      const response = await apiClient.post("/api/chat", {
        agent_id: agentId,
        message,
        history,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to send message" };
    }
  },

  getConversations: async () => {
    try {
      const response = await apiClient.get("/api/chat/conversations");
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to get conversations" };
    }
  },

  getConversation: async (conversationId) => {
    try {
      const response = await apiClient.get(
        `/api/chat/conversations/${conversationId}`,
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to get conversation" };
    }
  },
};

// API functions for agents
export const agentAPI = {
  getAgents: async () => {
    try {
      const response = await apiClient.get("/api/agents");
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to get agents" };
    }
  },

  getAgent: async (agentId) => {
    try {
      const response = await apiClient.get(`/api/agents/${agentId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to get agent" };
    }
  },

  createAgent: async (agentData) => {
    try {
      const response = await apiClient.post("/api/agents", agentData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to create agent" };
    }
  },

  updateAgent: async (agentId, agentData) => {
    try {
      const response = await apiClient.put(`/api/agents/${agentId}`, agentData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to update agent" };
    }
  },

  deleteAgent: async (agentId) => {
    try {
      const response = await apiClient.delete(`/api/agents/${agentId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to delete agent" };
    }
  },
};

// API functions for code execution
export const codeAPI = {
  executeCode: async (code, language, threadId, agentId) => {
    try {
      const response = await apiClient.post("/api/code/execute", {
        code,
        language,
        thread_id: threadId,
        agent_id: agentId,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to execute code" };
    }
  },

  writeFile: async (filePath, content, threadId, agentId) => {
    try {
      const response = await apiClient.post("/api/code/write-file", {
        file_path: filePath,
        content,
        thread_id: threadId,
        agent_id: agentId,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to write file" };
    }
  },

  readFile: async (filePath, threadId, agentId) => {
    try {
      const response = await apiClient.post("/api/code/read-file", {
        file_path: filePath,
        thread_id: threadId,
        agent_id: agentId,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to read file" };
    }
  },

  installPackages: async (packages, language, threadId, agentId) => {
    try {
      const response = await apiClient.post("/api/code/install-packages", {
        packages,
        language,
        thread_id: threadId,
        agent_id: agentId,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: "Failed to install packages" };
    }
  },
};

// Export all APIs
export const api = {
  auth: authAPI,
  chat: chatAPI,
  agent: agentAPI,
  code: codeAPI,
};

export default api;
