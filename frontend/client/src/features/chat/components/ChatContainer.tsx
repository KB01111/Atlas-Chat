import React, { useState, useEffect, useRef } from 'react';

import { supabase } from '../api-client';

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [agentType, setAgentType] = useState('default');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchInitialMessages = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data, error } = await supabase
          .from('messages')
          .select('*')
          .order('created_at', { ascending: true });
        if (error) throw error;
        setMessages(data || []);
      } catch (err: any) {
        setError('Failed to load chat messages.');
      }
      setLoading(false);
    };

    fetchInitialMessages();

    const channel = supabase
      .channel('chat-messages')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'messages' },
        (payload) => {
          setMessages((prev) => [...prev, payload.new]);
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const optimisticMessage = {
      id: Date.now(),
      content: newMessage,
      sender: 'You',
      created_at: new Date().toISOString(),
      agent_type: agentType,
    };
    setMessages((prev) => [...prev, optimisticMessage]);
    setNewMessage('');
    setSending(true);
    try {
      const { error } = await supabase.from('messages').insert([
        {
          content: optimisticMessage.content,
          sender: optimisticMessage.sender,
          agent_type: agentType,
        },
      ]);
      if (error) {
        setError('Failed to send message.');
      }
    } catch {
      setError('Network error while sending message.');
    }
    setSending(false);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div>
      <h2>Chat</h2>
      <label>
        Agent Type:
        <select value={agentType} onChange={(e) => setAgentType(e.target.value)}>
          <option value="default">Default</option>
          <option value="assistant">Assistant</option>
          <option value="system">System</option>
        </select>
      </label>
      {loading ? (
        <div>Loading chat...</div>
      ) : error ? (
        <div style={{ color: 'red' }}>{error}</div>
      ) : (
        <div
          style={{
            maxHeight: '400px',
            overflowY: 'auto',
            border: '1px solid #ccc',
            padding: '5px',
          }}
        >
          {messages.map((msg) => (
            <div key={msg.id} style={{ marginBottom: '8px' }}>
              <strong>{msg.sender || 'User'}</strong> [
              {new Date(msg.created_at).toLocaleTimeString()}] ({msg.agent_type || 'default'}):
              <br />
              {msg.content}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <input
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={sending}
        />
        <button type="submit" disabled={sending || !newMessage.trim()}>
          {sending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatContainer;
