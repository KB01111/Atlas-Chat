import React, { useEffect, useState } from 'react';
import VirtualizedChatList from './VirtualizedChatList';
import { api } from '../../api-client';
import { useParams } from 'react-router-dom';
import MessageInput from './MessageInput';
import MessageRenderer from './MessageRenderer';
import './ChatContainer.css';

/**
 * ChatContainer component with optimized rendering for long conversations
 * Integrates the VirtualizedChatList component for performance optimization
 */
const ChatContainer = () => {
  const { conversationId } = useParams();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMoreMessages, setHasMoreMessages] = useState(false);
  const [oldestMessageId, setOldestMessageId] = useState(null);
  const [error, setError] = useState(null);

  // Load initial messages
  useEffect(() => {
    if (conversationId) {
      loadConversation();
    }
  }, [conversationId]);

  // Load conversation messages
  const loadConversation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const conversation = await api.chat.getConversation(conversationId);
      
      setMessages(conversation.messages || []);
      setHasMoreMessages(conversation.has_more_messages || false);
      
      if (conversation.messages && conversation.messages.length > 0) {
        setOldestMessageId(conversation.messages[0].id);
      }
      
    } catch (err) {
      setError('Failed to load conversation');
      console.error('Error loading conversation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load more messages when scrolling up
  const loadMoreMessages = async () => {
    if (!hasMoreMessages || isLoadingMore || !oldestMessageId) return;
    
    try {
      setIsLoadingMore(true);
      
      const olderMessages = await api.chat.getConversationMessages(
        conversationId, 
        { before_id: oldestMessageId, limit: 50 }
      );
      
      if (olderMessages.messages && olderMessages.messages.length > 0) {
        setMessages(prev => [...olderMessages.messages, ...prev]);
        setOldestMessageId(olderMessages.messages[0].id);
        setHasMoreMessages(olderMessages.has_more_messages || false);
      } else {
        setHasMoreMessages(false);
      }
      
    } catch (err) {
      console.error('Error loading more messages:', err);
    } finally {
      setIsLoadingMore(false);
    }
  };

  // Send a new message
  const sendMessage = async (content) => {
    try {
      const newMessage = {
        id: `temp-${Date.now()}`,
        content,
        sender: 'user',
        timestamp: new Date().toISOString(),
        status: 'sending'
      };
      
      setMessages(prev => [...prev, newMessage]);
      
      const response = await api.chat.sendMessage(
        conversationId,
        content
      );
      
      // Replace temp message with actual message
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id ? { ...response.message, status: 'sent' } : msg
      ));
      
      // Add agent response
      if (response.reply) {
        setMessages(prev => [...prev, { ...response.reply, status: 'received' }]);
      }
      
    } catch (err) {
      // Mark message as failed
      setMessages(prev => prev.map(msg => 
        msg.id === `temp-${Date.now()}` ? { ...msg, status: 'failed' } : msg
      ));
      
      setError('Failed to send message');
      console.error('Error sending message:', err);
    }
  };

  // Render individual message
  const renderMessage = (message, index) => {
    return (
      <MessageRenderer 
        key={message.id || index}
        message={message}
        isLastMessage={index === messages.length - 1}
      />
    );
  };

  if (isLoading && messages.length === 0) {
    return <div className="loading-container">Loading conversation...</div>;
  }

  if (error && messages.length === 0) {
    return <div className="error-container">{error}</div>;
  }

  return (
    <div className="chat-container">
      <div className="messages-container">
        <VirtualizedChatList
          messages={messages}
          loadMoreMessages={loadMoreMessages}
          hasMoreMessages={hasMoreMessages}
          isLoadingMore={isLoadingMore}
          renderMessage={renderMessage}
        />
      </div>
      
      <div className="input-container">
        <MessageInput onSendMessage={sendMessage} />
      </div>
    </div>
  );
};

export default ChatContainer;
