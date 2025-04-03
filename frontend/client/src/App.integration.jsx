// This file integrates the pruned frontend with the AtlasChat backend
// It serves as the main integration point between the frontend and backend

import { ApiProvider } from './data-provider/simplified-api';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { useApi } from './data-provider/simplified-api';

// Import components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import AgentSelector from './components/AgentSelector';
import Chat from './components/Chat/Chat'; // Assuming this component exists

// Auth provider to handle authentication state
const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const api = useApi();
  
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await api.getCurrentUser();
        setIsAuthenticated(!!user);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, [api]);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return children({ isAuthenticated });
};

// Private route component
const PrivateRoute = ({ element }) => {
  return (
    <AuthProvider>
      {({ isAuthenticated }) => 
        isAuthenticated ? element : <Navigate to="/login" />
      }
    </AuthProvider>
  );
};

// Main App component
const App = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  
  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
  };
  
  return (
    <ApiProvider>
      <Router>
        <div className="app-container">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/" 
              element={
                <PrivateRoute 
                  element={
                    <div className="main-content">
                      <div className="sidebar">
                        <AgentSelector onSelect={handleAgentSelect} />
                      </div>
                      <div className="chat-container">
                        {selectedAgent ? (
                          <Chat agentId={selectedAgent.agent_id} />
                        ) : (
                          <div className="select-agent-prompt">
                            Please select an agent to start chatting
                          </div>
                        )}
                      </div>
                    </div>
                  } 
                />
              } 
            />
          </Routes>
        </div>
      </Router>
    </ApiProvider>
  );
};

export default App;
