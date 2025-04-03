import React, { useState, useEffect } from 'react';
import { useApi } from '../data-provider/simplified-api';

// Simple component for selecting an agent
const AgentSelector = ({ onSelect }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  
  const api = useApi();
  
  // Fetch agents on component mount
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const agentList = await api.getAgents();
        setAgents(agentList);
        
        // Select the first agent by default if available
        if (agentList.length > 0 && !selectedAgentId) {
          setSelectedAgentId(agentList[0].agent_id);
          onSelect(agentList[0]);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching agents:', err);
        setError('Failed to load agents. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAgents();
  }, [api, onSelect, selectedAgentId]);
  
  // Handle agent selection
  const handleAgentChange = async (e) => {
    const agentId = e.target.value;
    setSelectedAgentId(agentId);
    
    try {
      const agentDetails = await api.getAgent(agentId);
      onSelect(agentDetails);
    } catch (err) {
      console.error(`Error fetching agent details for ${agentId}:`, err);
      setError('Failed to load agent details. Please try again later.');
    }
  };
  
  if (loading) {
    return <div className="text-gray-500">Loading agents...</div>;
  }
  
  if (error) {
    return <div className="text-red-500">{error}</div>;
  }
  
  if (agents.length === 0) {
    return <div className="text-gray-500">No agents available.</div>;
  }
  
  return (
    <div className="agent-selector">
      <label htmlFor="agent-select" className="block text-sm font-medium text-gray-700 mb-1">
        Select Agent
      </label>
      <select
        id="agent-select"
        value={selectedAgentId}
        onChange={handleAgentChange}
        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
      >
        {agents.map((agent) => (
          <option key={agent.agent_id} value={agent.agent_id}>
            {agent.name} - {agent.agent_type}
          </option>
        ))}
      </select>
      
      {selectedAgentId && (
        <div className="mt-2 text-xs text-gray-500">
          Using {agents.find(a => a.agent_id === selectedAgentId)?.agent_type} agent
        </div>
      )}
    </div>
  );
};

export default AgentSelector;
