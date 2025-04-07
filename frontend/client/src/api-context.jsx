import React, { createContext, useContext, useEffect, useState } from "react";
import api from "./api-client";

// Create context
const ApiContext = createContext(null);

// Provider component
export const ApiProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [conversations, setConversations] = useState([]);

  // Initialize - check if user is logged in
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem("atlaschat_token");
        if (token) {
          const userData = await api.auth.getCurrentUser();
          setUser(userData);

          // Load agents
          const agentsData = await api.agent.getAgents();
          setAgents(agentsData);

          // Set default agent if available
          if (agentsData.length > 0) {
            setSelectedAgent(agentsData[0].agent_id);
          }

          // Load conversations
          const conversationsData = await api.chat.getConversations();
          setConversations(conversationsData);
        }
      } catch (error) {
        console.error("Initialization error:", error);
        localStorage.removeItem("atlaschat_token");
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Authentication methods
  const login = async (email, password) => {
    setLoading(true);
    try {
      const result = await api.auth.login(email, password);
      setUser(result.user);

      // Load agents
      const agentsData = await api.agent.getAgents();
      setAgents(agentsData);

      // Set default agent if available
      if (agentsData.length > 0) {
        setSelectedAgent(agentsData[0].agent_id);
      }

      // Load conversations
      const conversationsData = await api.chat.getConversations();
      setConversations(conversationsData);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.detail || "Login failed" };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      await api.auth.register(name, email, password);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.detail || "Registration failed" };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.auth.logout();
    setUser(null);
    setAgents([]);
    setSelectedAgent(null);
    setConversations([]);
  };

  // Chat methods
  const sendMessage = async (message, history) => {
    if (!selectedAgent) {
      return { success: false, error: "No agent selected" };
    }

    try {
      const response = await api.chat.sendMessage(
        selectedAgent,
        message,
        history,
      );
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error.detail || "Failed to send message",
      };
    }
  };

  // Agent methods
  const selectAgent = (agentId) => {
    setSelectedAgent(agentId);
  };

  const refreshAgents = async () => {
    try {
      const agentsData = await api.agent.getAgents();
      setAgents(agentsData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.detail || "Failed to refresh agents",
      };
    }
  };

  // Code execution methods
  const executeCode = async (code, language, threadId) => {
    if (!selectedAgent) {
      return { success: false, error: "No agent selected" };
    }

    try {
      const response = await api.code.executeCode(
        code,
        language,
        threadId,
        selectedAgent,
      );
      return response;
    } catch (error) {
      return {
        success: false,
        error: error.detail || "Failed to execute code",
      };
    }
  };

  const writeFile = async (filePath, content, threadId) => {
    if (!selectedAgent) {
      return { success: false, error: "No agent selected" };
    }

    try {
      const response = await api.code.writeFile(
        filePath,
        content,
        threadId,
        selectedAgent,
      );
      return response;
    } catch (error) {
      return { success: false, error: error.detail || "Failed to write file" };
    }
  };

  const readFile = async (filePath, threadId) => {
    if (!selectedAgent) {
      return { success: false, error: "No agent selected" };
    }

    try {
      const response = await api.code.readFile(
        filePath,
        threadId,
        selectedAgent,
      );
      return response;
    } catch (error) {
      return { success: false, error: error.detail || "Failed to read file" };
    }
  };

  const installPackages = async (packages, language, threadId) => {
    if (!selectedAgent) {
      return { success: false, error: "No agent selected" };
    }

    try {
      const response = await api.code.installPackages(
        packages,
        language,
        threadId,
        selectedAgent,
      );
      return response;
    } catch (error) {
      return {
        success: false,
        error: error.detail || "Failed to install packages",
      };
    }
  };

  // Create value object with all methods and state
  const value = {
    // State
    user,
    loading,
    agents,
    selectedAgent,
    conversations,

    // Auth methods
    login,
    register,
    logout,

    // Chat methods
    sendMessage,

    // Agent methods
    selectAgent,
    refreshAgents,

    // Code execution methods
    executeCode,
    writeFile,
    readFile,
    installPackages,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

// Custom hook to use the API context
export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error("useApi must be used within an ApiProvider");
  }
  return context;
};

export default ApiContext;
